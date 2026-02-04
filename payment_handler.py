import os
import requests
import qrcode
import io
import base64
from typing import Optional, Dict
from dotenv import load_dotenv

load_dotenv()

MISTICPAY_CLIENT_ID = os.getenv("MISTICPAY_CLIENT_ID")
MISTICPAY_CLIENT_SECRET = os.getenv("MISTICPAY_CLIENT_SECRET")
MISTICPAY_API_URL = "https://api.misticpay.com/api"

class MisticPayHandler:
    """Gerenciador de pagamentos com MisticPay."""
    
    @staticmethod
    def create_payment_link(receiver_id: int, amount: float, description: str = "Cobrança", channel_id: int = None) -> Optional[Dict]:
        """Cria um link de pagamento MisticPay e retorna URL + QR Code."""
        try:
            print(f"[MisticPay] Iniciando criação de pagamento...")
            print(f"[MisticPay] Client ID: {MISTICPAY_CLIENT_ID}")
            
            headers = {
                "ci": MISTICPAY_CLIENT_ID,
                "cs": MISTICPAY_CLIENT_SECRET,
                "Content-Type": "application/json"
            }
            
            # Gerar ID de transação único
            import time
            transaction_id = f"discord_{receiver_id}_{int(time.time())}"
            
            payload = {
                "amount": amount,
                "payerName": f"Cliente {receiver_id}",
                "payerDocument": "00000000000",  # CPF genérico
                "transactionId": transaction_id,
                "description": description
            }
            
            print(f"[MisticPay] Enviando POST para: {MISTICPAY_API_URL}/transactions/create")
            print(f"[MisticPay] Payload: {payload}")
            
            response = requests.post(
                f"{MISTICPAY_API_URL}/transactions/create",
                json=payload,
                headers=headers,
                timeout=10
            )
            
            print(f"[MisticPay] Status Code: {response.status_code}")
            print(f"[MisticPay] Response: {response.text[:500]}")
            
            if response.status_code == 200 or response.status_code == 201:
                data = response.json()
                transaction_data = data.get("data", {})
                
                payment_id = transaction_data.get("transactionId")
                qr_code_base64 = transaction_data.get("qrCodeBase64")
                qr_code_url = transaction_data.get("qrcodeUrl")
                copy_paste = transaction_data.get("copyPaste")
                
                return {
                    "payment_id": payment_id,
                    "url": copy_paste,  # Código PIX copia e cola
                    "qr_code_url": qr_code_url,
                    "qr_code_base64": qr_code_base64,
                    "channel_id": channel_id,
                    "amount": amount
                }
            else:
                print(f"[MisticPay] ERRO: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"[MisticPay] EXCEÇÃO: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    @staticmethod
    def generate_qr_code(data: str) -> str:
        """Gera QR code em formato base64."""
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(data)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Converter para base64
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return img_str
        except Exception as e:
            print(f"Erro ao gerar QR code: {e}")
            return None
    
    @staticmethod
    def verify_webhook(request_body: Dict) -> Optional[Dict]:
        """Verifica e processa webhook de pagamento MisticPay."""
        try:
            print(f"[Webhook] Dados recebidos: {request_body}")
            
            event_type = request_body.get("event")
            print(f"[Webhook] Tipo de evento: {event_type}")
            
            # MisticPay pode enviar: transaction.paid, charge.paid, payment.approved, etc
            if event_type in ["transaction.paid", "charge.paid", "payment.approved", "transaction.approved"]:
                data_field = request_body.get("data", {})
                print(f"[Webhook] Data field: {data_field}")
                
                # Tentar obter payment_id de várias formas
                payment_id = (
                    data_field.get("transactionId") or 
                    data_field.get("id") or 
                    data_field.get("payment_id")
                )
                
                amount = data_field.get("amount", 0)
                
                # MisticPay não envia receiver_id no webhook, precisamos buscar no banco
                # Vamos usar o payment_id para encontrar o receiver
                from database import get_payment_receiver
                receiver_id = get_payment_receiver(payment_id)
                
                if not receiver_id:
                    print(f"[Webhook] ERRO: Receiver não encontrado para payment_id: {payment_id}")
                    return None
                
                print(f"[Webhook] ✅ Pagamento confirmado: {payment_id} | R$ {amount} | Receiver: {receiver_id}")
                
                return {
                    "payment_id": payment_id,
                    "receiver_id": receiver_id,
                    "amount": amount,
                    "status": "completed"
                }
            else:
                print(f"[Webhook] Evento ignorado: {event_type}")
            
            return None
        except Exception as e:
            print(f"Erro ao verificar webhook MisticPay: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    @staticmethod
    def create_withdrawal(user_id: int, amount: float, pix_key: str) -> Optional[Dict]:
        """Cria um saque/transferência PIX automática."""
        try:
            print(f"[MisticPay] Iniciando saque...")
            print(f"[MisticPay] Client ID: {MISTICPAY_CLIENT_ID}")
            
            headers = {
                "ci": MISTICPAY_CLIENT_ID,
                "cs": MISTICPAY_CLIENT_SECRET,
                "Content-Type": "application/json"
            }
            
            # Detectar tipo de chave PIX
            pix_key_type = "CHAVE_ALEATORIA"  # Default
            if "@" in pix_key:
                pix_key_type = "EMAIL"
            elif len(pix_key) == 11 and pix_key.isdigit():
                pix_key_type = "CPF"
            elif len(pix_key) == 14 and pix_key.isdigit():
                pix_key_type = "CNPJ"
            elif pix_key.startswith("+"):
                pix_key_type = "TELEFONE"
            
            payload = {
                "amount": amount,
                "pixKey": pix_key,
                "pixKeyType": pix_key_type,
                "description": f"Saque Discord - Usuário {user_id}"
            }
            
            print(f"[MisticPay] Enviando POST para: {MISTICPAY_API_URL}/transactions/withdraw")
            print(f"[MisticPay] Payload: {payload}")
            
            response = requests.post(
                f"{MISTICPAY_API_URL}/transactions/withdraw",
                json=payload,
                headers=headers,
                timeout=10
            )
            
            print(f"[MisticPay] Status Code: {response.status_code}")
            print(f"[MisticPay] Response: {response.text[:500]}")
            
            if response.status_code in [200, 201, 202]:  # 202 = Aceito (em processamento)
                data = response.json()
                withdrawal_data = data.get("data", {})
                
                return {
                    "payout_id": withdrawal_data.get("transactionId"),
                    "status": withdrawal_data.get("status", "QUEUED"),
                    "amount": amount
                }
            else:
                print(f"[MisticPay] ERRO no saque: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"[MisticPay] EXCEÇÃO no saque: {e}")
            import traceback
            traceback.print_exc()
            return None
            print(f"Erro ao criar saque: {e}")
            return None
