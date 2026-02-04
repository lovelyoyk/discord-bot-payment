"""
Suite de Testes para Pagamentos PIX
Testa integração com MisticPay em ambiente seguro
"""
import os
from payment_handler import MisticPayHandler

class PaymentTester:
    def __init__(self):
        self.handler = MisticPayHandler()
        self.test_results = []
    
    def log_result(self, test_name: str, success: bool, message: str):
        """Registra resultado do teste"""
        result = {
            'test': test_name,
            'success': success,
            'message': message
        }
        self.test_results.append(result)
        
        emoji = "✅" if success else "❌"
        print(f"{emoji} {test_name}: {message}")
    
    def test_create_payment_link(self):
        """Teste 1: Criar link de pagamento"""
        try:
            result = self.handler.create_payment_link(
                user_id=123456789,
                amount=1.00,  # R$ 1,00 para teste
                description="Teste de Pagamento"
            )
            
            if result and 'url' in result:
                self.log_result(
                    "Criar Link de Pagamento",
                    True,
                    f"Link criado: {result['payment_id']}"
                )
                return result
            else:
                self.log_result(
                    "Criar Link de Pagamento",
                    False,
                    "Falha ao criar link"
                )
                return None
        except Exception as e:
            self.log_result(
                "Criar Link de Pagamento",
                False,
                f"Erro: {str(e)}"
            )
            return None
    
    def test_check_payment_status(self, payment_id: str):
        """Teste 2: Verificar status de pagamento"""
        try:
            status = self.handler.check_payment_status(payment_id)
            
            if status:
                self.log_result(
                    "Verificar Status",
                    True,
                    f"Status obtido: {status}"
                )
                return status
            else:
                self.log_result(
                    "Verificar Status",
                    False,
                    "Falha ao obter status"
                )
                return None
        except Exception as e:
            self.log_result(
                "Verificar Status",
                False,
                f"Erro: {str(e)}"
            )
            return None
    
    def test_create_withdrawal(self):
        """Teste 3: Criar saque (CUIDADO: usa saldo real!)"""
        print("\n⚠️ ATENÇÃO: Este teste cria um saque REAL!")
        print("⚠️ Apenas execute se tiver saldo de teste na conta MisticPay")
        confirm = input("Digite 'CONFIRMAR' para continuar: ")
        
        if confirm != "CONFIRMAR":
            self.log_result(
                "Criar Saque",
                False,
                "Teste cancelado pelo usuário"
            )
            return None
        
        # Solicitar chave PIX de teste
        pix_key = input("Digite uma chave PIX válida para teste: ")
        
        try:
            result = self.handler.create_withdrawal(
                user_id=123456789,
                amount=1.00,  # R$ 1,00 para teste
                pix_key=pix_key
            )
            
            if result and 'payout_id' in result:
                self.log_result(
                    "Criar Saque",
                    True,
                    f"Saque criado: {result['payout_id']}"
                )
                return result
            else:
                self.log_result(
                    "Criar Saque",
                    False,
                    "Falha ao criar saque"
                )
                return None
        except Exception as e:
            self.log_result(
                "Criar Saque",
                False,
                f"Erro: {str(e)}"
            )
            return None
    
    def test_webhook_validation(self):
        """Teste 4: Validar webhook"""
        from utils.webhook_validator import webhook_validator
        
        # Payload de teste
        test_payload = '{"event":"payment.approved","data":{"payment_id":"test123"},"timestamp":1234567890}'
        test_signature = "test_signature"
        
        try:
            # Se não tiver secret configurado, só testa a estrutura
            import json
            data = json.loads(test_payload)
            
            is_valid = webhook_validator.validate_payload(data)
            
            self.log_result(
                "Validação de Webhook",
                is_valid,
                "Estrutura válida" if is_valid else "Estrutura inválida"
            )
        except Exception as e:
            self.log_result(
                "Validação de Webhook",
                False,
                f"Erro: {str(e)}"
            )
    
    def run_all_tests(self, include_withdrawal: bool = False):
        """Executa todos os testes"""
        print("\n" + "="*50)
        print("🧪 INICIANDO TESTES DE PAGAMENTO")
        print("="*50 + "\n")
        
        # Teste 1: Criar pagamento
        payment_result = self.test_create_payment_link()
        
        # Teste 2: Verificar status (se pagamento foi criado)
        if payment_result:
            self.test_check_payment_status(payment_result['payment_id'])
        
        # Teste 3: Saque (opcional)
        if include_withdrawal:
            self.test_create_withdrawal()
        
        # Teste 4: Webhook
        self.test_webhook_validation()
        
        # Resumo
        print("\n" + "="*50)
        print("📊 RESUMO DOS TESTES")
        print("="*50)
        
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r['success'])
        failed = total - passed
        
        print(f"\nTotal: {total} | Passou: {passed} | Falhou: {failed}")
        
        if failed > 0:
            print("\n❌ Testes que falharam:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['message']}")
        else:
            print("\n✅ Todos os testes passaram!")
        
        print("\n" + "="*50 + "\n")
        
        return passed == total


if __name__ == "__main__":
    tester = PaymentTester()
    
    print("Escolha o tipo de teste:")
    print("1 - Testes básicos (sem saque real)")
    print("2 - Todos os testes (INCLUI saque real)")
    
    choice = input("\nOpção: ")
    
    if choice == "2":
        tester.run_all_tests(include_withdrawal=True)
    else:
        tester.run_all_tests(include_withdrawal=False)
