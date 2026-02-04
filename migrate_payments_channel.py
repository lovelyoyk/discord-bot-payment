#!/usr/bin/env python3
"""
Migration: Adicionar coluna channel_id à tabela payments

Este script migra um banco de dados existente para incluir a coluna channel_id
que é necessária para as notificações em canal.

Uso:
    python migrate_payments_channel.py
"""

import sqlite3
import os
import shutil
from datetime import datetime

DB_PATH = "bot.db"

def backup_database():
    """Cria backup do banco de dados antes da migração."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"bot.db.backup_{timestamp}"
    
    if os.path.exists(DB_PATH):
        shutil.copy2(DB_PATH, backup_path)
        print(f"✅ Backup criado: {backup_path}")
        return backup_path
    return None

def check_column_exists():
    """Verifica se a coluna channel_id já existe."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(payments)")
        columns = cursor.fetchall()
        conn.close()
        
        column_names = [col[1] for col in columns]
        return "channel_id" in column_names
    except Exception as e:
        print(f"❌ Erro ao verificar colunas: {e}")
        return False

def migrate():
    """Executa a migração."""
    try:
        # Verificar se já foi migrado
        if check_column_exists():
            print("✅ Coluna channel_id já existe. Migração não necessária.")
            return True
        
        # Criar backup
        backup = backup_database()
        
        # Conectar ao banco
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print("⏳ Adicionando coluna channel_id...")
        
        # Adicionar coluna
        cursor.execute("""
            ALTER TABLE payments 
            ADD COLUMN channel_id INTEGER
        """)
        
        conn.commit()
        conn.close()
        
        print("✅ Migração concluída com sucesso!")
        print(f"   - Coluna 'channel_id' adicionada à tabela 'payments'")
        print(f"   - Backup salvo em: {backup}")
        return True
        
    except Exception as e:
        print(f"❌ Erro durante migração: {e}")
        print(f"   Seu backup foi salvo e o banco não foi alterado")
        return False

def verify_migration():
    """Verifica se a migração foi bem-sucedida."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Tentar inserir um registro teste
        cursor.execute("""
            INSERT INTO payments 
            (payment_id, receiver_id, amount, channel_id, status) 
            VALUES ('test_migration_123', 0, 0.0, NULL, 'test')
        """)
        
        # Verificar se foi inserido
        cursor.execute("SELECT channel_id FROM payments WHERE payment_id = 'test_migration_123'")
        result = cursor.fetchone()
        
        # Remover registro teste
        cursor.execute("DELETE FROM payments WHERE payment_id = 'test_migration_123'")
        conn.commit()
        conn.close()
        
        if result is not None:
            print("✅ Verificação passou: Coluna channel_id está funcionando!")
            return True
        else:
            print("❌ Verificação falhou: Não foi possível acessar channel_id")
            return False
            
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
        return False

def main():
    print("=" * 50)
    print("🔄 Migração de Banco de Dados")
    print("=" * 50)
    print()
    
    # Verificar se o banco existe
    if not os.path.exists(DB_PATH):
        print("⚠️  Banco de dados não encontrado em:", DB_PATH)
        print("   Se você está iniciando pela primeira vez, isso é normal.")
        print("   O banco será criado automaticamente na próxima inicialização.")
        return
    
    print(f"📁 Banco de dados: {DB_PATH}")
    print()
    
    # Executar migração
    if migrate():
        print()
        
        # Verificar migração
        if verify_migration():
            print()
            print("=" * 50)
            print("✅ Tudo pronto! Você pode reiniciar o bot.")
            print("=" * 50)
        else:
            print()
            print("⚠️  Migração concluída, mas verificação falhou.")
            print("   Verifique os logs para mais detalhes.")
    else:
        print()
        print("=" * 50)
        print("❌ Migração falhou. Seu banco não foi alterado.")
        print("=" * 50)

if __name__ == "__main__":
    main()
