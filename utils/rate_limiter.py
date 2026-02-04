"""
Sistema de Rate Limiting
Proteção contra spam de comandos
"""
import time
from collections import defaultdict
from typing import Dict, Tuple

class RateLimiter:
    def __init__(self):
        # user_id -> (timestamp, count)
        self.user_commands: Dict[int, list] = defaultdict(list)
        self.cooldowns: Dict[str, Dict[int, float]] = defaultdict(dict)
    
    def check_rate_limit(self, user_id: int, command: str, max_per_minute: int = 10) -> Tuple[bool, int]:
        """
        Verifica se usuário está dentro do rate limit
        
        Returns:
            (permitido: bool, tempo_restante: int)
        """
        now = time.time()
        
        # Limpar comandos antigos (mais de 1 minuto)
        self.user_commands[user_id] = [
            timestamp for timestamp in self.user_commands[user_id]
            if now - timestamp < 60
        ]
        
        # Verificar quantidade de comandos no último minuto
        if len(self.user_commands[user_id]) >= max_per_minute:
            # Calcular tempo restante
            oldest_command = min(self.user_commands[user_id])
            time_remaining = int(60 - (now - oldest_command))
            return False, time_remaining
        
        # Adicionar comando atual
        self.user_commands[user_id].append(now)
        return True, 0
    
    def check_cooldown(self, user_id: int, command: str, cooldown_seconds: int = 5) -> Tuple[bool, int]:
        """
        Verifica cooldown específico de um comando
        
        Returns:
            (permitido: bool, tempo_restante: int)
        """
        now = time.time()
        
        # Verificar último uso do comando
        if command in self.cooldowns and user_id in self.cooldowns[command]:
            last_use = self.cooldowns[command][user_id]
            time_passed = now - last_use
            
            if time_passed < cooldown_seconds:
                time_remaining = int(cooldown_seconds - time_passed)
                return False, time_remaining
        
        # Atualizar último uso
        self.cooldowns[command][user_id] = now
        return True, 0
    
    def reset_user(self, user_id: int):
        """Reseta rate limit de um usuário (admin use)"""
        if user_id in self.user_commands:
            del self.user_commands[user_id]
        
        for command_dict in self.cooldowns.values():
            if user_id in command_dict:
                del command_dict[user_id]
    
    def get_user_stats(self, user_id: int) -> dict:
        """Retorna estatísticas de uso de um usuário"""
        now = time.time()
        recent_commands = [
            timestamp for timestamp in self.user_commands[user_id]
            if now - timestamp < 60
        ]
        
        return {
            'commands_last_minute': len(recent_commands),
            'active_cooldowns': sum(
                1 for cmd_dict in self.cooldowns.values()
                if user_id in cmd_dict and now - cmd_dict[user_id] < 60
            )
        }

# Instância global
rate_limiter = RateLimiter()
