"""
Migração: Adicionar coluna internal_id na tabela payments
"""
import sqlite3

DB_PATH = "./data/bot.db"

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Verificar se a coluna já existe
        cursor.execute("PRAGMA table_info(payments)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'internal_id' not in columns:
            print("Adicionando coluna internal_id...")
            cursor.execute("ALTER TABLE payments ADD COLUMN internal_id TEXT")
            conn.commit()
            print("✅ Coluna internal_id adicionada com sucesso!")
        else:
            print("✅ Coluna internal_id já existe!")
        
    except Exception as e:
        print(f"❌ Erro na migração: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
