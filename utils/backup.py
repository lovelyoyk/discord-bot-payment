"""
Sistema de Backup Automático do Banco de Dados
Cria backups incrementais e mantém histórico
"""
import os
import shutil
from datetime import datetime, timedelta
import schedule
import time
import threading

class BackupManager:
    def __init__(self, db_path: str, backup_dir: str = "./backups", keep_days: int = 30):
        self.db_path = db_path
        self.backup_dir = backup_dir
        self.keep_days = keep_days
        
        # Criar diretório de backup se não existir
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
    
    def create_backup(self):
        """Cria um backup do banco de dados"""
        try:
            # Nome do arquivo de backup com timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"bot_backup_{timestamp}.db"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            # Copiar arquivo
            shutil.copy2(self.db_path, backup_path)
            
            print(f"✅ Backup criado: {backup_filename}")
            
            # Limpar backups antigos
            self.cleanup_old_backups()
            
            return True
        except Exception as e:
            print(f"❌ Erro ao criar backup: {e}")
            return False
    
    def cleanup_old_backups(self):
        """Remove backups mais antigos que keep_days"""
        try:
            now = datetime.now()
            cutoff_date = now - timedelta(days=self.keep_days)
            
            for filename in os.listdir(self.backup_dir):
                if filename.startswith("bot_backup_") and filename.endswith(".db"):
                    file_path = os.path.join(self.backup_dir, filename)
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    if file_time < cutoff_date:
                        os.remove(file_path)
                        print(f"🗑️ Backup antigo removido: {filename}")
        except Exception as e:
            print(f"⚠️ Erro ao limpar backups antigos: {e}")
    
    def restore_backup(self, backup_filename: str):
        """Restaura um backup específico"""
        try:
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            if not os.path.exists(backup_path):
                print(f"❌ Backup não encontrado: {backup_filename}")
                return False
            
            # Criar backup do arquivo atual antes de restaurar
            current_backup = f"bot_backup_before_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            shutil.copy2(self.db_path, os.path.join(self.backup_dir, current_backup))
            
            # Restaurar
            shutil.copy2(backup_path, self.db_path)
            print(f"✅ Backup restaurado: {backup_filename}")
            return True
        except Exception as e:
            print(f"❌ Erro ao restaurar backup: {e}")
            return False
    
    def list_backups(self):
        """Lista todos os backups disponíveis"""
        backups = []
        for filename in os.listdir(self.backup_dir):
            if filename.startswith("bot_backup_") and filename.endswith(".db"):
                file_path = os.path.join(self.backup_dir, filename)
                file_size = os.path.getsize(file_path)
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                backups.append({
                    'filename': filename,
                    'size': file_size,
                    'date': file_time
                })
        
        # Ordenar por data (mais recente primeiro)
        backups.sort(key=lambda x: x['date'], reverse=True)
        return backups
    
    def start_scheduled_backups(self, hour: int = 3, minute: int = 0):
        """Inicia backups automáticos agendados"""
        # Agendar backup diário
        schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(self.create_backup)
        
        # Também fazer backup a cada 6 horas
        schedule.every(6).hours.do(self.create_backup)
        
        def run_schedule():
            while True:
                schedule.run_pending()
                time.sleep(60)  # Verificar a cada minuto
        
        # Executar em thread separada
        backup_thread = threading.Thread(target=run_schedule, daemon=True)
        backup_thread.start()
        
        print(f"📅 Backups automáticos agendados: Diário às {hour:02d}:{minute:02d} e a cada 6 horas")
        
        # Criar backup inicial
        self.create_backup()
