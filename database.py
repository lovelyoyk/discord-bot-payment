import sqlite3
import os
from datetime import datetime
import threading

DB_PATH = os.getenv("DATABASE_PATH", "./data/bot.db")

# Lock para evitar race conditions em transações
_transaction_lock = threading.Lock()

def init_db():
    """Inicializa o banco de dados com as tabelas."""
    os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tabela de usuários e saldos (cada pessoa tem seu próprio saldo)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            balance REAL DEFAULT 0,
            pix_key TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Tabela de transações
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
    """)
    
    # Tabela de pagamentos MisticPay
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            payment_id TEXT PRIMARY KEY,
            receiver_id INTEGER NOT NULL,
            payer_id INTEGER,
            amount REAL NOT NULL,
            status TEXT DEFAULT 'pending',
            qr_code TEXT,
            misticpay_id TEXT,
            channel_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(receiver_id) REFERENCES users(user_id)
        )
    """)
    
    # Tabela de saques
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS withdrawals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            status TEXT DEFAULT 'pending',
            pix_key TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            processed_at TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
    """)
    
    # Tabela de permissões de cargos para cobrar
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cargo_permissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role_id INTEGER UNIQUE NOT NULL,
            can_charge BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Tabela de histórico detalhado de transações
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transaction_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            amount REAL NOT NULL,
            gross_amount REAL,
            description TEXT,
            sender_id INTEGER,
            sender_name TEXT,
            misticpay_ref TEXT,
            status TEXT DEFAULT 'completed',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
    """)
    
    # Tabela de reembolsos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS refunds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            payment_id TEXT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            reason TEXT,
            misticpay_ref TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            processed_at TIMESTAMP,
            approved_by INTEGER,
            approved_at TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
    """)

    # Migração leve: garantir colunas de aprovação em bases antigas
    try:
        cursor.execute("PRAGMA table_info(refunds)")
        refund_columns = {row[1] for row in cursor.fetchall()}
        if "approved_by" not in refund_columns:
            cursor.execute("ALTER TABLE refunds ADD COLUMN approved_by INTEGER")
        if "approved_at" not in refund_columns:
            cursor.execute("ALTER TABLE refunds ADD COLUMN approved_at TIMESTAMP")
    except Exception as e:
        print(f"Erro ao verificar/migrar colunas de reembolso: {e}")
    
    # Tabela de financeiros (usuários com permissão para aprovar saques/reembolsos)
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS financeiros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                role TEXT DEFAULT 'financeiro',
                permissions TEXT DEFAULT 'approve_withdrawals,approve_refunds',
                added_by INTEGER,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        """)
    except Exception as e:
        print(f"Erro ao criar tabela financeiros: {e}")
    
    conn.commit()
    conn.close()

def add_user(user_id: int, pix_key: str = None) -> bool:
    """Adiciona um novo usuário se não existir."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT OR IGNORE INTO users (user_id, balance, pix_key) VALUES (?, ?, ?)", 
                      (user_id, 0, pix_key))
        conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao adicionar usuário: {e}")
        return False
    finally:
        conn.close()

def set_pix_key(user_id: int, pix_key: str) -> bool:
    """Define a chave PIX de um usuário."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE users SET pix_key = ? WHERE user_id = ?", (pix_key, user_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao definir chave PIX: {e}")
        return False
    finally:
        conn.close()

def get_pix_key(user_id: int) -> str:
    """Retorna a chave PIX de um usuário."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT pix_key FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result and result[0] else None

def get_balance(user_id: int) -> float:
    """Retorna o saldo de um usuário."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

def get_total_balance() -> float:
    """Retorna o saldo total de todos os usuários."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(balance) FROM users")
    result = cursor.fetchone()
    conn.close()
    return result[0] if result[0] else 0

def get_balance_by_user(user_id: int) -> dict:
    """Retorna info completa do usuário."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, balance, pix_key FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return {"user_id": result[0], "balance": result[1], "pix_key": result[2]}
    return None

def add_balance(user_id: int, amount: float, description: str = "Adição de saldo") -> bool:
    """Adiciona saldo a um usuário."""
    add_user(user_id)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
        cursor.execute("INSERT INTO transactions (user_id, type, amount, description) VALUES (?, ?, ?, ?)", 
                      (user_id, "add", amount, description))
        conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao adicionar saldo: {e}")
        return False
    finally:
        conn.close()

def remove_balance(user_id: int, amount: float, description: str = "Remoção de saldo") -> bool:
    """Remove saldo de um usuário (apenas admin)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    
    if not result or result[0] < amount:
        conn.close()
        return False
    
    try:
        cursor.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (amount, user_id))
        cursor.execute("INSERT INTO transactions (user_id, type, amount, description) VALUES (?, ?, ?, ?)", 
                      (user_id, "remove", amount, description))
        conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao remover saldo: {e}")
        return False
    finally:
        conn.close()

def withdraw_balance(user_id: int, amount: float) -> bool:
    """Processa um saque (simula transferência bancária)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    
    if not result or result[0] < amount:
        conn.close()
        return False
    
    try:
        cursor.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (amount, user_id))
        cursor.execute("INSERT INTO transactions (user_id, type, amount, description) VALUES (?, ?, ?, ?)", 
                      (user_id, "withdraw", amount, "Saque solicitado"))
        conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao sacar: {e}")
        return False
    finally:
        conn.close()

def get_transaction_history(user_id: int, limit: int = 10) -> list:
    """Retorna o histórico de transações de um usuário."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT type, amount, description, created_at 
        FROM transactions 
        WHERE user_id = ? 
        ORDER BY created_at DESC 
        LIMIT ?
    """, (user_id, limit))
    results = cursor.fetchall()
    conn.close()
    return results

def register_payment(payment_id: str, receiver_id: int, amount: float, channel_id: int = None, internal_id: str = None) -> bool:
    """Registra um pagamento com o canal onde foi gerado e o ID interno da MisticPay."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO payments (payment_id, receiver_id, amount, channel_id, internal_id, status)
            VALUES (?, ?, ?, ?, ?, 'pending')
        """, (payment_id, receiver_id, amount, channel_id, internal_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao registrar pagamento: {e}")
        return False
    finally:
        conn.close()

def get_payment_channel(payment_id: str) -> int:
    """Retorna o canal_id de um pagamento."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT channel_id FROM payments WHERE payment_id = ?", (payment_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def get_payment_receiver(payment_id: str) -> int:
    """Retorna o receiver_id (vendedor) de um pagamento.
    Procura tanto pelo payment_id customizado quanto pelo internal_id da MisticPay.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Primeiro tenta pelo payment_id customizado (discord_...)
    cursor.execute("SELECT receiver_id FROM payments WHERE payment_id = ?", (payment_id,))
    result = cursor.fetchone()
    
    # Se não encontrar, tenta pelo internal_id (ID numérico da MisticPay)
    if not result:
        cursor.execute("SELECT receiver_id FROM payments WHERE internal_id = ?", (payment_id,))
        result = cursor.fetchone()
    
    conn.close()
    return result[0] if result else None

def update_payment_status(payment_id: str, status: str) -> bool:
    """Atualiza status de um pagamento."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE payments SET status = ? WHERE payment_id = ?", (status, payment_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao atualizar pagamento: {e}")
        return False
    finally:
        conn.close()
# ════════════════════════════════════════════════════════════════════════════
# FUNÇÕES DE PERMISSÕES DE CARGO
# ════════════════════════════════════════════════════════════════════════════

def add_cargo_permission(role_id: int) -> bool:
    """Adiciona permissão de cobrar para um cargo."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT OR REPLACE INTO cargo_permissions (role_id, can_charge, updated_at)
            VALUES (?, 1, CURRENT_TIMESTAMP)
        """, (role_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao adicionar permissão de cargo: {e}")
        return False
    finally:
        conn.close()

def remove_cargo_permission(role_id: int) -> bool:
    """Remove permissão de cobrar de um cargo."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM cargo_permissions WHERE role_id = ?", (role_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao remover permissão de cargo: {e}")
        return False
    finally:
        conn.close()

def has_cargo_permission(role_id: int) -> bool:
    """Verifica se um cargo tem permissão de cobrar."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT can_charge FROM cargo_permissions WHERE role_id = ?", (role_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else False
    except Exception as e:
        print(f"Erro ao verificar permissão de cargo: {e}")
        return False

def get_all_cargo_permissions() -> list:
    """Retorna todos os cargos com permissão."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT role_id FROM cargo_permissions WHERE can_charge = 1")
        return [row[0] for row in cursor.fetchall()]
    except Exception as e:
        print(f"Erro ao listar permissões de cargo: {e}")
        return []
    finally:
        conn.close()

# ════════════════════════════════════════════════════════════════════════════
# FUNÇÕES DE HISTÓRICO DETALHADO DE TRANSAÇÕES
# ════════════════════════════════════════════════════════════════════════════

def add_transaction_history(
    user_id: int, 
    transaction_type: str, 
    amount: float,
    description: str,
    gross_amount: float = None,
    sender_id: int = None,
    sender_name: str = None,
    misticpay_ref: str = None,
    status: str = "completed"
) -> bool:
    """Adiciona uma transação ao histórico detalhado."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO transaction_history 
            (user_id, type, amount, gross_amount, description, sender_id, sender_name, misticpay_ref, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, transaction_type, amount, gross_amount, description, sender_id, sender_name, misticpay_ref, status))
        conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao adicionar histórico de transação: {e}")
        return False
    finally:
        conn.close()

def get_transaction_history_detailed(user_id: int, limit: int = 10) -> list:
    """Retorna o histórico detalhado de transações de um usuário."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT type, amount, gross_amount, description, sender_name, misticpay_ref, status, created_at
            FROM transaction_history
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (user_id, limit))
        return cursor.fetchall()
    except Exception as e:
        print(f"Erro ao buscar histórico: {e}")
        return []
    finally:
        conn.close()

# ════════════════════════════════════════════════════════════════════════════
# FUNÇÕES DE REEMBOLSO
# ════════════════════════════════════════════════════════════════════════════

def create_refund(
    user_id: int,
    amount: float,
    reason: str,
    payment_id: str = None,
    misticpay_ref: str = None
) -> bool:
    """Cria um reembolso."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO refunds (payment_id, user_id, amount, reason, misticpay_ref, status)
            VALUES (?, ?, ?, ?, ?, 'pending')
        """, (payment_id, user_id, amount, reason, misticpay_ref))
        conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao criar reembolso: {e}")
        return False
    finally:
        conn.close()

def process_refund(refund_id: int, misticpay_ref: str = None) -> bool:
    """Marca um reembolso como processado."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE refunds 
            SET status = 'completed', processed_at = CURRENT_TIMESTAMP, misticpay_ref = ?
            WHERE id = ?
        """, (misticpay_ref, refund_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao processar reembolso: {e}")
        return False
    finally:
        conn.close()

def approve_refund(refund_id: int, approved_by: int) -> bool:
    """Aprova um reembolso pendente."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        # Verificar se o reembolso existe
        cursor.execute("SELECT id, status FROM refunds WHERE id = ?", (refund_id,))
        refund = cursor.fetchone()
        print(f"[DEBUG] Reembolso encontrado: {refund}")
        
        if not refund:
            print(f"[ERRO] Reembolso #{refund_id} não encontrado no banco")
            return False
        
        if refund[1] != 'pending':
            print(f"[ERRO] Reembolso #{refund_id} já foi processado. Status atual: {refund[1]}")
            return False
        
        cursor.execute("""
            UPDATE refunds 
            SET status = 'aprovado', approved_by = ?, approved_at = CURRENT_TIMESTAMP
            WHERE id = ? AND status = 'pending'
        """, (approved_by, refund_id))
        conn.commit()
        
        rows_affected = cursor.rowcount
        print(f"[DEBUG] Linhas afetadas: {rows_affected}")
        return rows_affected > 0
    except Exception as e:
        print(f"Erro ao aprovar reembolso: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

def reject_refund(refund_id: int, approved_by: int) -> bool:
    """Rejeita um reembolso pendente."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE refunds 
            SET status = 'rejeitado', approved_by = ?, approved_at = CURRENT_TIMESTAMP
            WHERE id = ? AND status = 'pending'
        """, (approved_by, refund_id))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Erro ao rejeitar reembolso: {e}")
        return False
    finally:
        conn.close()

def get_refund_by_id(refund_id: int) -> dict:
    """Retorna os dados de um reembolso específico."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, user_id, amount, reason, status, created_at, approved_by, approved_at
            FROM refunds
            WHERE id = ?
        """, (refund_id,))
        row = cursor.fetchone()
        if row:
            return {
                'id': row[0],
                'user_id': row[1],
                'amount': row[2],
                'reason': row[3],
                'status': row[4],
                'created_at': row[5],
                'approved_by': row[6],
                'approved_at': row[7]
            }
        return None
    except Exception as e:
        print(f"Erro ao buscar reembolso: {e}")
        return None
    finally:
        conn.close()

def get_pending_refunds() -> list:
    """Retorna todos os reembolsos pendentes."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, user_id, amount, reason, payment_id, created_at
            FROM refunds
            WHERE status = 'pending'
            ORDER BY created_at DESC
        """)
        return cursor.fetchall()
    except Exception as e:
        print(f"Erro ao listar reembolsos: {e}")
        return []
    finally:
        conn.close()

# ════════════════════════════════════════════════════════════════════════════
# FUNÇÕES DE TRANSAÇÃO COM LOCK (ANTI-RACE CONDITIONS)
# ════════════════════════════════════════════════════════════════════════════

def safe_add_balance(user_id: int, amount: float, description: str = "Adição de saldo") -> bool:
    """
    Adiciona saldo de forma segura, evitando race conditions com múltiplos usuários.
    Usa lock para garantir que a operação seja atômica.
    """
    with _transaction_lock:
        add_user(user_id)
        conn = sqlite3.connect(DB_PATH)
        
        # Ativar modo de transação com isolamento mais forte
        conn.isolation_level = None  # Modo autocommit desativado
        conn.execute("BEGIN IMMEDIATE")  # Lock de escrita imediato
        
        cursor = conn.cursor()
        try:
            # Verificar saldo atual (com lock)
            cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            current_balance = result[0] if result else 0
            
            # Atualizar saldo
            new_balance = current_balance + amount
            cursor.execute("UPDATE users SET balance = ?, updated_at = ? WHERE user_id = ?", 
                          (new_balance, datetime.now().isoformat(), user_id))
            
            # Registrar transação
            cursor.execute("""
                INSERT INTO transactions (user_id, type, amount, description)
                VALUES (?, ?, ?, ?)
            """, (user_id, "add", amount, description))
            
            # Registrar no histórico detalhado
            cursor.execute("""
                INSERT INTO transaction_history (user_id, type, amount, description, status)
                VALUES (?, ?, ?, ?, 'completed')
            """, (user_id, "add", amount, description))
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Erro ao adicionar saldo com segurança: {e}")
            return False
        finally:
            conn.close()

def safe_remove_balance(user_id: int, amount: float, description: str = "Remoção de saldo") -> bool:
    """
    Remove saldo de forma segura, evitando overdraft com múltiplos usuários simultâneos.
    Usa lock para garantir que a operação seja atômica.
    """
    with _transaction_lock:
        conn = sqlite3.connect(DB_PATH)
        
        # Ativar modo de transação com isolamento mais forte
        conn.isolation_level = None
        conn.execute("BEGIN IMMEDIATE")
        
        cursor = conn.cursor()
        try:
            # Verificar saldo com lock
            cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            
            if not result or result[0] < amount:
                conn.rollback()
                return False
            
            current_balance = result[0]
            new_balance = current_balance - amount
            
            # Atualizar saldo
            cursor.execute("UPDATE users SET balance = ?, updated_at = ? WHERE user_id = ?", 
                          (new_balance, datetime.now().isoformat(), user_id))
            
            # Registrar transação
            cursor.execute("""
                INSERT INTO transactions (user_id, type, amount, description)
                VALUES (?, ?, ?, ?)
            """, (user_id, "remove", amount, description))
            
            # Registrar no histórico detalhado
            cursor.execute("""
                INSERT INTO transaction_history (user_id, type, amount, description, status)
                VALUES (?, ?, ?, ?, 'completed')
            """, (user_id, "remove", amount, description))
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Erro ao remover saldo com segurança: {e}")
            return False
        finally:
            conn.close()

def safe_transfer_balance(from_user_id: int, to_user_id: int, amount: float, description: str = "Transferência") -> bool:
    """
    Transfere saldo entre dois usuários de forma segura.
    Evita race conditions e garante atomicidade.
    """
    with _transaction_lock:
        add_user(from_user_id)
        add_user(to_user_id)
        
        conn = sqlite3.connect(DB_PATH)
        conn.isolation_level = None
        conn.execute("BEGIN IMMEDIATE")
        
        cursor = conn.cursor()
        try:
            # Verificar saldo do remetente
            cursor.execute("SELECT balance FROM users WHERE user_id = ?", (from_user_id,))
            result = cursor.fetchone()
            
            if not result or result[0] < amount:
                conn.rollback()
                return False
            
            # Remover do remetente
            cursor.execute("UPDATE users SET balance = balance - ?, updated_at = ? WHERE user_id = ?", 
                          (amount, datetime.now().isoformat(), from_user_id))
            
            # Adicionar ao destinatário
            cursor.execute("UPDATE users SET balance = balance + ?, updated_at = ? WHERE user_id = ?", 
                          (amount, datetime.now().isoformat(), to_user_id))
            
            # Registrar transações
            cursor.execute("""
                INSERT INTO transactions (user_id, type, amount, description)
                VALUES (?, ?, ?, ?)
            """, (from_user_id, "transfer_out", amount, description))
            
            cursor.execute("""
                INSERT INTO transactions (user_id, type, amount, description)
                VALUES (?, ?, ?, ?)
            """, (to_user_id, "transfer_in", amount, description))
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Erro ao transferir saldo com segurança: {e}")
            return False
        finally:
            conn.close()

def safe_withdraw_balance(user_id: int, amount: float) -> bool:
    """
    Processa um saque de forma segura.
    Evita múltiplas solicitações simultâneas criarem overdraft.
    """
    with _transaction_lock:
        conn = sqlite3.connect(DB_PATH)
        conn.isolation_level = None
        conn.execute("BEGIN IMMEDIATE")
        
        cursor = conn.cursor()
        try:
            # Verificar saldo com lock
            cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            
            if not result or result[0] < amount:
                conn.rollback()
                return False
            
            # Atualizar saldo
            cursor.execute("UPDATE users SET balance = balance - ?, updated_at = ? WHERE user_id = ?", 
                          (amount, datetime.now().isoformat(), user_id))
            
            # Registrar como saque
            cursor.execute("""
                INSERT INTO transactions (user_id, type, amount, description)
                VALUES (?, ?, ?, ?)
            """, (user_id, "withdraw", amount, "Saque solicitado"))
            
            # Registrar no histórico detalhado
            cursor.execute("""
                INSERT INTO transaction_history (user_id, type, amount, description, status)
                VALUES (?, ?, ?, ?, 'completed')
            """, (user_id, "withdraw", amount, "Saque solicitado"))
            
            # Registrar em withdrawals
            cursor.execute("""
                INSERT INTO withdrawals (user_id, amount, status, pix_key)
                SELECT user_id, ?, 'pending', pix_key FROM users WHERE user_id = ?
            """, (amount, user_id))
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Erro ao sacar com segurança: {e}")
            return False
        finally:
            conn.close()

def get_transaction_lock_status() -> dict:
    """Retorna o status de locks de transação para debug."""
    return {
        "locked": _transaction_lock.locked(),
        "timestamp": datetime.now().isoformat()
    }

# ============ FUNÇÕES DE FINANCEIROS ============

def add_financeiro(user_id: int, added_by: int) -> bool:
    """Adiciona um usuário como financeiro (pode aprovar saques/reembolsos)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT OR REPLACE INTO financeiros (user_id, added_by, added_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """, (user_id, added_by))
        conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao adicionar financeiro: {e}")
        return False
    finally:
        conn.close()

def remove_financeiro(user_id: int) -> bool:
    """Remove um usuário da lista de financeiros."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM financeiros WHERE user_id = ?", (user_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Erro ao remover financeiro: {e}")
        return False
    finally:
        conn.close()

def is_financeiro(user_id: int) -> bool:
    """Verifica se um usuário é financeiro."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT 1 FROM financeiros WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        return result is not None
    except Exception as e:
        print(f"Erro ao verificar se é financeiro: {e}")
        return False
    finally:
        conn.close()

def get_all_financeiros() -> list:
    """Retorna lista de todos os financeiros."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT user_id FROM financeiros ORDER BY added_at DESC")
        result = cursor.fetchall()
        return [row[0] for row in result]
    except Exception as e:
        print(f"Erro ao buscar financeiros: {e}")
        return []
    finally:
        conn.close()

def get_financeiro_info(user_id: int) -> dict:
    """Retorna informações sobre um financeiro."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT user_id, role, permissions, added_by, added_at
            FROM financeiros WHERE user_id = ?
        """, (user_id,))
        result = cursor.fetchone()
        if result:
            return {
                "user_id": result[0],
                "role": result[1],
                "permissions": result[2],
                "added_by": result[3],
                "added_at": result[4]
            }
        return None
    except Exception as e:
        print(f"Erro ao buscar info do financeiro: {e}")
        return None
    finally:
        conn.close()
