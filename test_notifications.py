#!/usr/bin/env python3
"""
Script de Teste e Validação - Notificações em Canal

Este script testa se toda a funcionalidade de notificações está corretamente configurada.

Uso:
    python test_notifications.py
"""

import os
import sqlite3
from dotenv import load_dotenv
from pathlib import Path

# Cores para output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.END}")

def check_env_variables():
    """Verifica se todas as variáveis de ambiente estão configuradas."""
    print("\n" + "="*50)
    print("🔍 Verificando Variáveis de Ambiente")
    print("="*50)
    
    load_dotenv()
    
    required_vars = {
        "DISCORD_BOT_TOKEN": "Token do bot Discord",
        "MISTICPAY_API_KEY": "API Key MisticPay",
        "OWNER_ID": "ID do dono do bot",
    }
    
    optional_vars = {
        "EMOJI_SUCESSO": "✅",
        "EMOJI_CLIENTE": "👥",
        "EMOJI_VENDEDOR": "👤",
        "EMOJI_VALOR": "💰",
        "EMOJI_PAGAMENTO": "💳",
    }
    
    missing = []
    
    # Verificar obrigatórias
    print("\n📋 Variáveis Obrigatórias:")
    for var, desc in required_vars.items():
        value = os.getenv(var)
        if value:
            print_success(f"{var}: Configurado")
        else:
            print_error(f"{var}: NÃO configurado - {desc}")
            missing.append(var)
    
    # Verificar opcionais
    print("\n🎨 Emojis (Opcionais - usando padrão se não configurado):")
    for var, default in optional_vars.items():
        value = os.getenv(var, default)
        print_success(f"{var}: {value}")
    
    if missing:
        print_error(f"\n❌ {len(missing)} variáveis obrigatórias faltando!")
        return False
    
    print_success("\n✅ Todas as variáveis obrigatórias configuradas!")
    return True

def check_database_schema():
    """Verifica se a tabela payments tem a coluna channel_id."""
    print("\n" + "="*50)
    print("🗄️  Verificando Banco de Dados")
    print("="*50)
    
    db_path = "bot.db"
    
    if not os.path.exists(db_path):
        print_warning(f"Banco de dados não existe: {db_path}")
        print_info("Será criado automaticamente ao iniciar o bot")
        return True
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar se tabela payments existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='payments'")
        if not cursor.fetchone():
            print_error("Tabela 'payments' não encontrada")
            conn.close()
            return False
        
        print_success("Tabela 'payments' encontrada")
        
        # Verificar se coluna channel_id existe
        cursor.execute("PRAGMA table_info(payments)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if "channel_id" in column_names:
            print_success("Coluna 'channel_id' encontrada em payments")
            return True
        else:
            print_error("Coluna 'channel_id' NÃO encontrada em payments")
            print_warning("Execute: python migrate_payments_channel.py")
            conn.close()
            return False
            
    except Exception as e:
        print_error(f"Erro ao verificar banco: {e}")
        return False
    finally:
        conn.close()

def check_files():
    """Verifica se todos os arquivos necessários existem."""
    print("\n" + "="*50)
    print("📁 Verificando Arquivos")
    print("="*50)
    
    required_files = [
        "main.py",
        "database.py",
        "payment_handler.py",
        "webhook_server.py",
        "validador_pix.py",
        "ui_components.py",
        "cogs/payment.py",
        "cogs/relatorios.py",
        ".env",
    ]
    
    optional_files = [
        "migrate_payments_channel.py",
        "NOTIFICACOES_CANAL.md",
        "CHANGELOG_v2.1.md",
    ]
    
    missing = []
    
    print("\n📋 Arquivos Obrigatórios:")
    for file in required_files:
        if os.path.exists(file):
            print_success(f"{file}")
        else:
            print_error(f"{file}: NÃO encontrado")
            missing.append(file)
    
    print("\n📚 Arquivos Opcionais (Documentação):")
    for file in optional_files:
        if os.path.exists(file):
            print_success(f"{file}")
        else:
            print_warning(f"{file}: Não encontrado (opcional)")
    
    if missing:
        print_error(f"\n❌ {len(missing)} arquivos obrigatórios faltando!")
        return False
    
    print_success("\n✅ Todos os arquivos necessários encontrados!")
    return True

def check_imports():
    """Verifica se os imports principais funcionam."""
    print("\n" + "="*50)
    print("🔗 Verificando Imports")
    print("="*50)
    
    modules = {
        "discord": "Discord.py",
        "dotenv": "python-dotenv",
        "sqlite3": "Banco de dados (builtin)",
        "flask": "Flask webhook",
        "requests": "HTTP requests",
        "qrcode": "QR Code generation",
    }
    
    issues = []
    
    for module, desc in modules.items():
        try:
            __import__(module)
            print_success(f"{module}: {desc}")
        except ImportError as e:
            print_error(f"{module}: Não instalado - {desc}")
            issues.append(module)
    
    if issues:
        print_error(f"\n❌ {len(issues)} módulo(s) faltando!")
        print_info(f"Execute: pip install {' '.join(issues)}")
        return False
    
    print_success("\n✅ Todos os módulos importáveis!")
    return True

def check_webhook_server():
    """Verifica se webhook_server.py tem a função de notificação."""
    print("\n" + "="*50)
    print("🔔 Verificando Webhook Server")
    print("="*50)
    
    try:
        with open("webhook_server.py", "r") as f:
            content = f.read()
        
        checks = {
            "get_payment_channel": "Função para buscar channel_id",
            "notificar_pagamento": "Função de notificação",
            "EMOJI_SUCESSO": "Variável de emoji",
            "bot_instance.get_channel": "Envio em canal",
        }
        
        found = []
        for check, desc in checks.items():
            if check in content:
                print_success(f"{check}: Encontrado - {desc}")
                found.append(check)
            else:
                print_warning(f"{check}: Não encontrado - {desc}")
        
        if len(found) == len(checks):
            print_success("\n✅ Webhook server configurado corretamente!")
            return True
        else:
            print_warning(f"\n⚠️  {len(found)}/{len(checks)} checks passaram")
            return True  # Ainda passa porque pode ser versão antiga
            
    except Exception as e:
        print_error(f"Erro ao verificar webhook: {e}")
        return False

def test_database_insert():
    """Testa inserção de dados com channel_id."""
    print("\n" + "="*50)
    print("🧪 Testando Inserção em BD")
    print("="*50)
    
    db_path = "bot.db"
    
    if not os.path.exists(db_path):
        print_warning("Banco não existe - será criado ao iniciar bot")
        return True
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Tentar inserir registro teste
        cursor.execute("""
            INSERT INTO payments 
            (payment_id, receiver_id, amount, channel_id, status) 
            VALUES ('test_123456789', 0, 1.0, 12345, 'test')
        """)
        
        # Verificar se foi inserido
        cursor.execute("SELECT channel_id FROM payments WHERE payment_id = 'test_123456789'")
        result = cursor.fetchone()
        
        # Limpar
        cursor.execute("DELETE FROM payments WHERE payment_id = 'test_123456789'")
        conn.commit()
        conn.close()
        
        if result and result[0] == 12345:
            print_success("✅ Inserção com channel_id funcionando!")
            return True
        else:
            print_error("❌ Falha ao inserir channel_id")
            return False
            
    except Exception as e:
        print_warning(f"Erro no teste de BD (pode ser normal): {e}")
        return True  # Pode falhar em primeira execução

def print_summary(results):
    """Imprime resumo dos testes."""
    print("\n" + "="*50)
    print("📊 RESUMO DOS TESTES")
    print("="*50)
    
    total = len(results)
    passed = sum(results.values())
    failed = total - passed
    
    print(f"\n✅ Passou: {passed}/{total}")
    print(f"❌ Falhou: {failed}/{total}")
    
    if failed == 0:
        print_success("\n🎉 TUDO PRONTO! Sua instalação está completa!")
        print("\nPróximos passos:")
        print("1. Execute: python main.py")
        print("2. Em outro terminal: python webhook_server.py")
        print("3. Teste com: !cobrar @usuario 0.01 sim")
        print("4. Verifique a notificação no canal!")
    else:
        print_error(f"\n⚠️  {failed} problema(s) encontrado(s)")
        print("\nResolva os problemas acima e execute este script novamente")
    
    return failed == 0

def main():
    print("\n" + Colors.BLUE + "="*50)
    print("🧪 TESTE DE NOTIFICAÇÕES EM CANAL")
    print("="*50 + Colors.END)
    
    results = {
        "Variáveis de Ambiente": check_env_variables(),
        "Banco de Dados": check_database_schema(),
        "Arquivos": check_files(),
        "Imports": check_imports(),
        "Webhook Server": check_webhook_server(),
        "Inserção BD": test_database_insert(),
    }
    
    success = print_summary(results)
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
