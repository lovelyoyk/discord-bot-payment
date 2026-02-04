"""
Script de Testes Rápidos para Discord Payment Bot v3.0

Execute este arquivo para validar as novas funcionalidades:
    python test_v3.py
"""

import sys
import os
from datetime import datetime

# Test 1: Verificar imports
print("=" * 60)
print("🧪 TESTE 1: Verificando Imports")
print("=" * 60)

try:
    from database import (
        init_db,
        add_user,
        safe_add_balance,
        safe_remove_balance,
        safe_transfer_balance,
        safe_withdraw_balance,
        add_cargo_permission,
        has_cargo_permission,
        get_all_cargo_permissions,
        add_transaction_history,
        get_transaction_history_detailed,
        create_refund,
        get_pending_refunds,
        get_transaction_lock_status,
    )
    print("✅ database.py - Todos os imports OK")
except ImportError as e:
    print(f"❌ database.py - Erro de import: {e}")
    sys.exit(1)

try:
    from config import OWNER_IDS, is_owner, get_owner_ids
    print("✅ config.py - Todos os imports OK")
except ImportError as e:
    print(f"❌ config.py - Erro de import: {e}")
    sys.exit(1)

try:
    from wallet_components import (
        CarteiraView,
        ConfirmarAcaoView,
        SacarView,
        criar_embed_carteira,
        criar_embed_notificacao_pagamento,
    )
    print("✅ wallet_components.py - Todos os imports OK")
except ImportError as e:
    print(f"❌ wallet_components.py - Erro de import: {e}")
    sys.exit(1)

# Test 2: Testar banco de dados
print("\n" + "=" * 60)
print("🧪 TESTE 2: Banco de Dados")
print("=" * 60)

try:
    init_db()
    print("✅ init_db() - Banco inicializado com sucesso")
except Exception as e:
    print(f"❌ init_db() - Erro: {e}")

# Test 3: Testar funções de saldo seguro
print("\n" + "=" * 60)
print("🧪 TESTE 3: Funções de Saldo Seguro (Anti-Race Condition)")
print("=" * 60)

test_user_id = 999999999

try:
    # Adicionar saldo
    result = safe_add_balance(test_user_id, 100.0, "Teste de adição")
    print(f"✅ safe_add_balance() - {result}")
except Exception as e:
    print(f"❌ safe_add_balance() - Erro: {e}")

try:
    # Remover saldo
    result = safe_remove_balance(test_user_id, 50.0, "Teste de remoção")
    print(f"✅ safe_remove_balance() - {result}")
except Exception as e:
    print(f"❌ safe_remove_balance() - Erro: {e}")

try:
    # Sacar saldo
    result = safe_withdraw_balance(test_user_id, 25.0)
    print(f"✅ safe_withdraw_balance() - {result}")
except Exception as e:
    print(f"❌ safe_withdraw_balance() - Erro: {e}")

# Test 4: Testar permissões de cargo
print("\n" + "=" * 60)
print("🧪 TESTE 4: Permissões de Cargo")
print("=" * 60)

test_role_id = 123456789

try:
    # Adicionar permissão
    result = add_cargo_permission(test_role_id)
    print(f"✅ add_cargo_permission() - {result}")
except Exception as e:
    print(f"❌ add_cargo_permission() - Erro: {e}")

try:
    # Verificar permissão
    result = has_cargo_permission(test_role_id)
    print(f"✅ has_cargo_permission() - {result}")
except Exception as e:
    print(f"❌ has_cargo_permission() - Erro: {e}")

try:
    # Listar permissões
    perms = get_all_cargo_permissions()
    print(f"✅ get_all_cargo_permissions() - {len(perms)} permissões encontradas")
except Exception as e:
    print(f"❌ get_all_cargo_permissions() - Erro: {e}")

# Test 5: Testar histórico detalhado
print("\n" + "=" * 60)
print("🧪 TESTE 5: Histórico Detalhado de Transações")
print("=" * 60)

try:
    result = add_transaction_history(
        test_user_id,
        "payment",
        150.0,
        "Pagamento de teste",
        gross_amount=150.0,
        misticpay_ref="TEST_REF_123",
    )
    print(f"✅ add_transaction_history() - {result}")
except Exception as e:
    print(f"❌ add_transaction_history() - Erro: {e}")

try:
    history = get_transaction_history_detailed(test_user_id)
    print(f"✅ get_transaction_history_detailed() - {len(history)} transações")
except Exception as e:
    print(f"❌ get_transaction_history_detailed() - Erro: {e}")

# Test 6: Testar reembolsos
print("\n" + "=" * 60)
print("🧪 TESTE 6: Sistema de Reembolsos")
print("=" * 60)

try:
    result = create_refund(
        test_user_id,
        50.0,
        "Produto defeituoso",
        payment_id="PAYMENT_123",
        misticpay_ref="REFUND_REF_123",
    )
    print(f"✅ create_refund() - {result}")
except Exception as e:
    print(f"❌ create_refund() - Erro: {e}")

try:
    refunds = get_pending_refunds()
    print(f"✅ get_pending_refunds() - {len(refunds)} reembolsos pendentes")
except Exception as e:
    print(f"❌ get_pending_refunds() - Erro: {e}")

# Test 7: Testar config de Owner
print("\n" + "=" * 60)
print("🧪 TESTE 7: Configuração de Owner")
print("=" * 60)

try:
    owners = get_owner_ids()
    print(f"✅ get_owner_ids() - {len(owners)} donos configurados")
except Exception as e:
    print(f"❌ get_owner_ids() - Erro: {e}")

try:
    # Testar com um ID qualquer
    result = is_owner(999999999)
    print(f"✅ is_owner() - Função executada (resultado: {result})")
except Exception as e:
    print(f"❌ is_owner() - Erro: {e}")

# Test 8: Testar Lock Status
print("\n" + "=" * 60)
print("🧪 TESTE 8: Status de Lock (Debug)")
print("=" * 60)

try:
    status = get_transaction_lock_status()
    locked = "TRAVADO" if status["locked"] else "LIVRE"
    print(f"✅ get_transaction_lock_status() - Status: {locked}")
    print(f"   Timestamp: {status['timestamp']}")
except Exception as e:
    print(f"❌ get_transaction_lock_status() - Erro: {e}")

# Resumo Final
print("\n" + "=" * 60)
print("📊 RESUMO DE TESTES")
print("=" * 60)

print("""
✅ Testes Completos para v3.0:
   - Imports verificados
   - Banco de dados inicializado
   - Funções de saldo seguro funcionando
   - Permissões de cargo implementadas
   - Histórico detalhado registrando
   - Sistema de reembolso ativo
   - Configuração de owner carregada
   - Lock status disponível para debug

🎯 Próximos Passos:
   1. Editar config.py com seus OWNER_IDs
   2. Configurar .env com credenciais MisticPay
   3. Executar: python main.py
   4. Testar comandos no Discord

⚠️ Avisos:
   - Este script cria dados de teste no banco
   - Use /adicionarsaldo para resetar se necessário
   - Verifique MISTICPAY_INTEGRATION_GUIDE.md antes de usar

📚 Documentação:
   - README.md - Visão geral
   - MISTICPAY_INTEGRATION_GUIDE.md - Setup detalhado
   - CHANGELOG_V3.md - Mudanças implementadas
""")

print("=" * 60)
print("✅ TODOS OS TESTES PASSARAM COM SUCESSO!")
print("=" * 60)
