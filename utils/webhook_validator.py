"""
Validação de Webhooks MisticPay
Verifica assinaturas e autenticidade dos webhooks
"""
import hmac
import hashlib
import json
import os
from typing import Optional

class WebhookValidator:
    def __init__(self, secret_key: Optional[str] = None):
        """
        Inicializa validador de webhook
        
        Args:
            secret_key: Chave secreta do MisticPay (da dashboard)
        """
        self.secret_key = secret_key or os.getenv("MISTICPAY_WEBHOOK_SECRET", "")
    
    def validate_signature(self, payload: str, signature: str) -> bool:
        """
        Valida assinatura HMAC do webhook
        
        Args:
            payload: Corpo da requisição (JSON string)
            signature: Header X-Signature ou similar
            
        Returns:
            True se válido, False caso contrário
        """
        if not self.secret_key:
            print("⚠️ WEBHOOK_SECRET não configurado - Validação desabilitada")
            return True  # Permitir em dev, bloquear em produção
        
        try:
            # Calcular HMAC
            expected_signature = hmac.new(
                self.secret_key.encode('utf-8'),
                payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            # Comparação segura contra timing attacks
            return hmac.compare_digest(expected_signature, signature)
        except Exception as e:
            print(f"❌ Erro ao validar assinatura: {e}")
            return False
    
    def validate_payload(self, data: dict) -> bool:
        """
        Valida estrutura do payload
        
        Args:
            data: Dados do webhook parseados
            
        Returns:
            True se estrutura válida
        """
        required_fields = ['event', 'data']
        
        # Verificar campos obrigatórios
        for field in required_fields:
            if field not in data:
                print(f"❌ Campo obrigatório ausente: {field}")
                return False
        
        # Validar tipo de evento
        valid_events = ['payment.approved', 'payment.pending', 'payment.failed', 'payout.completed', 'payout.failed']
        if data['event'] not in valid_events:
            print(f"⚠️ Tipo de evento desconhecido: {data['event']}")
            return False
        
        return True
    
    def validate_timestamp(self, timestamp: int, max_age_seconds: int = 300) -> bool:
        """
        Valida se webhook não é muito antigo (proteção contra replay attacks)
        
        Args:
            timestamp: Unix timestamp do evento
            max_age_seconds: Idade máxima permitida (padrão: 5 minutos)
            
        Returns:
            True se timestamp válido
        """
        import time
        current_time = int(time.time())
        age = current_time - timestamp
        
        if age > max_age_seconds:
            print(f"⚠️ Webhook muito antigo: {age}s (máx: {max_age_seconds}s)")
            return False
        
        if age < -60:  # Timestamp no futuro (tolerância de 1 minuto)
            print(f"⚠️ Timestamp inválido: no futuro")
            return False
        
        return True
    
    def validate_webhook(self, payload: str, signature: str, data: dict) -> bool:
        """
        Validação completa do webhook
        
        Returns:
            True se webhook válido e seguro
        """
        # 1. Validar assinatura
        if not self.validate_signature(payload, signature):
            print("❌ Assinatura inválida")
            return False
        
        # 2. Validar estrutura
        if not self.validate_payload(data):
            print("❌ Payload inválido")
            return False
        
        # 3. Validar timestamp (se presente)
        if 'timestamp' in data:
            if not self.validate_timestamp(data['timestamp']):
                print("❌ Timestamp inválido")
                return False
        
        return True

# Instância global
webhook_validator = WebhookValidator()
