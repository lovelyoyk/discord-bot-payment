"""
Monitor de Uptime e Saúde do Bot
Envia alertas se bot cair ou tiver problemas
"""
import time
import requests
import threading
from datetime import datetime
import os

class UptimeMonitor:
    def __init__(self, webhook_url: str = None, check_interval: int = 60):
        """
        Monitor de uptime do bot
        
        Args:
            webhook_url: URL do webhook Discord para alertas
            check_interval: Intervalo de verificação em segundos
        """
        self.webhook_url = webhook_url or os.getenv("UPTIME_WEBHOOK_URL")
        self.check_interval = check_interval
        self.last_heartbeat = time.time()
        self.start_time = time.time()
        self.is_running = False
        self.error_count = 0
        self.last_error_time = None
    
    def heartbeat(self):
        """Atualiza heartbeat (chamar regularmente)"""
        self.last_heartbeat = time.time()
    
    def send_alert(self, title: str, message: str, color: int = 0xFF0000):
        """Envia alerta via webhook Discord"""
        if not self.webhook_url:
            return
        
        try:
            embed = {
                "title": title,
                "description": message,
                "color": color,
                "timestamp": datetime.utcnow().isoformat(),
                "footer": {"text": "Uptime Monitor"}
            }
            
            payload = {"embeds": [embed]}
            
            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status()
        except Exception as e:
            print(f"❌ Erro ao enviar alerta: {e}")
    
    def check_health(self):
        """Verifica saúde do bot"""
        now = time.time()
        time_since_heartbeat = now - self.last_heartbeat
        
        # Se passou muito tempo sem heartbeat (2x o intervalo)
        if time_since_heartbeat > (self.check_interval * 2):
            self.send_alert(
                "⚠️ Bot Sem Resposta",
                f"Bot não responde há {int(time_since_heartbeat)}s\n"
                f"Último heartbeat: {datetime.fromtimestamp(self.last_heartbeat).strftime('%H:%M:%S')}",
                color=0xFFA500  # Laranja
            )
    
    def log_error(self, error: Exception):
        """Registra erro e envia alerta se necessário"""
        self.error_count += 1
        self.last_error_time = time.time()
        
        # Enviar alerta se muitos erros em pouco tempo
        if self.error_count >= 5:
            self.send_alert(
                "❌ Múltiplos Erros Detectados",
                f"Bot teve {self.error_count} erros recentes\n"
                f"Último erro: {str(error)[:200]}",
                color=0xFF0000  # Vermelho
            )
            self.error_count = 0  # Reset
    
    def get_uptime(self) -> str:
        """Retorna tempo de uptime formatado"""
        uptime_seconds = int(time.time() - self.start_time)
        
        days = uptime_seconds // 86400
        hours = (uptime_seconds % 86400) // 3600
        minutes = (uptime_seconds % 3600) // 60
        seconds = uptime_seconds % 60
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m {seconds}s"
    
    def start_monitoring(self):
        """Inicia monitoramento em background"""
        if self.is_running:
            return
        
        self.is_running = True
        
        def monitor_loop():
            while self.is_running:
                self.check_health()
                time.sleep(self.check_interval)
        
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        
        # Enviar alerta de inicialização
        self.send_alert(
            "✅ Bot Iniciado",
            "Bot está online e monitoramento ativo",
            color=0x00FF00  # Verde
        )
        
        print(f"📊 Monitor de uptime iniciado (intervalo: {self.check_interval}s)")
    
    def stop_monitoring(self):
        """Para monitoramento"""
        self.is_running = False
        
        # Enviar alerta de desligamento
        self.send_alert(
            "🔴 Bot Desligado",
            f"Bot foi desligado após {self.get_uptime()} de uptime",
            color=0xFF0000  # Vermelho
        )

# Instância global
uptime_monitor = UptimeMonitor()
