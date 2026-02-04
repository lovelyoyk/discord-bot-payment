#!/usr/bin/env python3
"""
Simulador de Webhook para Testes Locais

Use este script para simular pagamentos sem precisar fazer pagamentos reais.

Funcionalidade:
1. Simula um pagamento MisticPay confirmado
2. Envia dados para o webhook local
3. Valida que notificação foi processada

Uso:
    python simulate_webhook.py [payment_id] [receiver_id] [channel_id] [amount]
    
Exemplos:
    python simulate_webhook.py pay_test_123 123456789 987654321 50.00
    python simulate_webhook.py pay_demo_001 999888777 555666777 100.00
"""

import requests
import json
import sys
import time
from datetime import datetime

# Cores para output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.END}")

def print_header(msg):
    print(f"\n{Colors.PURPLE}{'='*50}{Colors.END}")
    print(f"{Colors.PURPLE}{msg}{Colors.END}")
    print(f"{Colors.PURPLE}{'='*50}{Colors.END}\n")

def create_webhook_payload(payment_id, receiver_id, channel_id, amount):
    """Cria um payload simulado de webhook do MisticPay."""
    
    return {
        "id": f"evt_{int(time.time())}",
        "type": "charge.paid",
        "data": {
            "id": payment_id,
            "status": "paid",
            "amount": amount,
            "currency": "BRL",
            "pix_dict_key": "00000000-0000-0000-0000-000000000000",
            "metadata": {
                "receiver_id": receiver_id,
                "channel_id": channel_id,
                "type": "discord_payment"
            },
            "created_at": datetime.now().isoformat(),
            "paid_at": datetime.now().isoformat()
        }
    }

def send_webhook(webhook_url, payload):
    """Envia o payload para o webhook local."""
    try:
        headers = {
            "Content-Type": "application/json",
            "X-Signature": "test_signature_123"  # Pode ser vazio se WEBHOOK_SECRET não estiver setado
        }
        
        print_info(f"Enviando para: {webhook_url}")
        print_info(f"Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        
        response = requests.post(
            webhook_url,
            json=payload,
            headers=headers,
            timeout=5
        )
        
        return response
        
    except requests.exceptions.ConnectionError:
        print_error("Não foi possível conectar ao webhook!")
        print_info("Certifique-se que flask server está rodando:")
        print_info("  python webhook_server.py")
        return None
    except Exception as e:
        print_error(f"Erro ao enviar webhook: {e}")
        return None

def validate_response(response):
    """Valida a resposta do webhook."""
    if not response:
        return False
    
    try:
        if response.status_code == 200:
            data = response.json()
            print_success(f"Webhook processado com sucesso!")
            print_info(f"Resposta: {json.dumps(data, indent=2, ensure_ascii=False)}")
            return True
        else:
            print_error(f"Status inesperado: {response.status_code}")
            print_error(f"Resposta: {response.text}")
            return False
    except Exception as e:
        print_error(f"Erro ao processar resposta: {e}")
        return False

def get_user_input():
    """Pega inputs do usuário interativamente."""
    print_header("Simulador de Webhook MisticPay")
    
    print("Por favor, insira os valores para simular um pagamento:\n")
    
    # Payment ID
    payment_id = input(f"{Colors.BLUE}Payment ID{Colors.END} (ex: pay_test_123): ").strip()
    if not payment_id:
        payment_id = f"pay_test_{int(time.time())}"
    
    # Receiver ID
    while True:
        receiver_id_input = input(f"{Colors.BLUE}ID do Receptor (Discord){Colors.END} (seu ID): ").strip()
        if receiver_id_input.isdigit():
            receiver_id = int(receiver_id_input)
            break
        else:
            print_error("Por favor insira um número válido")
    
    # Channel ID
    while True:
        channel_id_input = input(f"{Colors.BLUE}ID do Canal (Discord){Colors.END}: ").strip()
        if channel_id_input.isdigit():
            channel_id = int(channel_id_input)
            break
        else:
            print_error("Por favor insira um número válido")
    
    # Amount
    while True:
        try:
            amount = float(input(f"{Colors.BLUE}Valor (R$){Colors.END} (ex: 50.00): ").strip())
            if amount > 0:
                break
            else:
                print_error("Valor deve ser maior que 0")
        except ValueError:
            print_error("Por favor insira um número válido")
    
    return payment_id, receiver_id, channel_id, amount

def main():
    print_header("🎲 Simulador de Webhook de Pagamento")
    
    # Pegar argumentos ou input do usuário
    if len(sys.argv) >= 5:
        # Argumentos da linha de comando
        payment_id = sys.argv[1]
        receiver_id = int(sys.argv[2])
        channel_id = int(sys.argv[3])
        amount = float(sys.argv[4])
        print_info(f"Usando argumentos da linha de comando")
    else:
        # Input interativo
        payment_id, receiver_id, channel_id, amount = get_user_input()
    
    print("\n" + "="*50)
    print("📊 Dados da Simulação:")
    print("="*50)
    print(f"  Payment ID:  {payment_id}")
    print(f"  Receptor:    {receiver_id}")
    print(f"  Canal:       {channel_id}")
    print(f"  Valor:       R$ {amount:.2f}")
    print("="*50)
    
    # Criar payload
    print_info("Criando payload de webhook...")
    payload = create_webhook_payload(payment_id, receiver_id, channel_id, amount)
    print_success("Payload criado")
    
    # Enviar webhook
    print_info("Enviando webhook para localhost:5000...")
    response = send_webhook("http://localhost:5000/webhook", payload)
    
    # Validar resposta
    print("\n" + "="*50)
    if response:
        success = validate_response(response)
        if success:
            print_success("Simulação completada com sucesso!")
            print("\n✅ Verificações:")
            print("  1. Verifique o saldo: !saldo")
            print("  2. Verifique o canal: Procure pela notificação")
            print("  3. Verifique DM privada: Procure a confirmação do bot")
        else:
            print_error("Falha na validação da resposta")
    else:
        print_error("Não foi possível completar a simulação")
    print("="*50)

def test_mode():
    """Executa série de testes."""
    print_header("🧪 Modo de Teste Automático")
    
    tests = [
        ("pay_test_001", 123456789, 987654321, 10.00),
        ("pay_test_002", 111222333, 444555666, 25.50),
        ("pay_test_003", 999888777, 555666777, 100.00),
    ]
    
    print_info(f"Executando {len(tests)} testes...\n")
    
    passed = 0
    for i, (payment_id, receiver_id, channel_id, amount) in enumerate(tests, 1):
        print(f"\n{Colors.PURPLE}Teste {i}/{len(tests)}{Colors.END}")
        print("-" * 30)
        
        payload = create_webhook_payload(payment_id, receiver_id, channel_id, amount)
        response = send_webhook("http://localhost:5000/webhook", payload)
        
        if response and validate_response(response):
            passed += 1
            print_success("Teste passou")
        else:
            print_error("Teste falhou")
        
        time.sleep(1)  # Pequeno delay entre testes
    
    print("\n" + "="*50)
    print(f"📊 Resultado: {passed}/{len(tests)} testes passaram")
    print("="*50)

if __name__ == "__main__":
    if "--test" in sys.argv:
        test_mode()
    elif "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__)
    else:
        main()
