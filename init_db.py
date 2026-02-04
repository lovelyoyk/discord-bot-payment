import sqlite3
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Tabela de pagamentos
cursor.execute("""
CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    vendedor_id INTEGER,
    valor REAL,
    status TEXT,
    created_at TEXT,
    ref TEXT
)
""")

# Tabela de reembolsos
cursor.execute("""
CREATE TABLE IF NOT EXISTS refunds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    payment_id INTEGER,
    motivo TEXT,
    valor REAL,
    status TEXT DEFAULT 'pendente',
    created_at TEXT,
    approved_by INTEGER,
    approved_at TEXT
)
""")

# Tabela de usuários
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    nome TEXT,
    email TEXT,
    chave_pix TEXT,
    saldo REAL,
    vendedor INTEGER DEFAULT 0
)
""")

# Tabela de transações
cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    tipo TEXT,
    valor REAL,
    status TEXT,
    created_at TEXT,
    ref TEXT
)
""")

conn.commit()
conn.close()
print("✅ Banco de dados inicializado com sucesso!")
