# 📢 Notificações de Pagamento no Canal

## Overview

O bot agora envia notificações de pagamento confirmado **diretamente no canal Discord** onde o comando `/cobrar` foi executado, com **emojis personalizáveis**.

## Como Funciona

### 1. **Fluxo de Notificação**

```
Usuário executa !cobrar @cliente 100 sim
        ↓
Bot cria link MisticPay com channel_id
        ↓
Usuário paga via link
        ↓
Webhook MisticPay é acionado
        ↓
Bot busca channel_id da transação
        ↓
Bot envia embed no canal com emojis personalizados
        ↓
Vendedor recebe DM confirmar recebimento
```

### 2. **Armazenamento do Canal**

- Quando `!cobrar` é executado, o `channel_id` do canal atual é capturado
- O ID é passado para a API MisticPay via metadados
- Quando o pagamento é confirmado, o webhook recupera o channel_id
- A notificação é enviada para esse canal específico

### 3. **Emojis Personalizáveis**

Configure no arquivo `.env`:

```env
# Emojis das notificações
EMOJI_SUCESSO=✅
EMOJI_CLIENTE=👥
EMOJI_VENDEDOR=👤
EMOJI_VALOR=💰
EMOJI_PAGAMENTO=💳
```

## Exemplos de Configuração

### Tema Profissional
```env
EMOJI_SUCESSO=☑️
EMOJI_CLIENTE=💼
EMOJI_VENDEDOR=👨‍💼
EMOJI_VALOR=💵
EMOJI_PAGAMENTO=🏦
```

### Tema Divertido
```env
EMOJI_SUCESSO=🎉
EMOJI_CLIENTE=🤝
EMOJI_VENDEDOR=😎
EMOJI_VALOR=🤑
EMOJI_PAGAMENTO=🎁
```

### Tema Minimalista
```env
EMOJI_SUCESSO=✓
EMOJI_CLIENTE=■
EMOJI_VENDEDOR=●
EMOJI_VALOR=$
EMOJI_PAGAMENTO=→
```

## Comandos Relacionados

### Ver Configuração de Emojis
```bash
!config_emojis
```

Mostra todos os emojis atualmente configurados. **Apenas o dono do bot pode usar.**

## Banco de Dados

### Coluna `channel_id` na Tabela `payments`

A tabela `payments` foi atualizada com:

```sql
CREATE TABLE payments (
    payment_id TEXT PRIMARY KEY,
    receiver_id INTEGER,
    payer_id INTEGER,
    amount REAL,
    status TEXT,
    qr_code TEXT,
    misticpay_id TEXT,
    channel_id INTEGER,  -- ← NOVO: Armazena ID do canal
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Exemplo de Notificação

### Antes (DM privada)
```
[DM do Bot]
✅ Pagamento Recebido
💰 Valor: R$ 100.00
📌 ID: pay_abc123
```

### Agora (Canal Público + DM)

**No canal:**
```
✅ Pagamento Confirmado
Cobrança foi paga com sucesso!

👤 Vendedor: @VendedorNome
💰 Valor: R$ 100.00
💳 ID da Transação: pay_abc123

Saldo foi creditado automaticamente
```

**DM do bot:**
```
✅ Pagamento Recebido
💰 Valor: R$ 100.00
📌 ID: pay_abc123

Saldo creditado automaticamente
```

## Migração de Banco de Dados

Se você já tem um `bot.db` existente, precisa fazer backup e recriar:

```powershell
# Windows PowerShell
Move-Item bot.db bot.db.backup
# O bot criará uma nova base automáticamente
```

Ou edite manualmente:
```sql
ALTER TABLE payments ADD COLUMN channel_id INTEGER;
```

## Fluxo Técnico Completo

### 1. Comando `/cobrar`
```python
# Em: cogs/payment.py
result = self.payment_handler.create_payment_link(
    cliente.id, 
    total,
    f"Cobrança de {ctx.author.name}",
    channel_id=ctx.channel.id  # ← Captura o canal
)

register_payment(
    payment_id=result['payment_id'],
    receiver_id=cliente.id,
    amount=total,
    channel_id=ctx.channel.id  # ← Armazena no BD
)
```

### 2. Criação de Link
```python
# Em: payment_handler.py
def create_payment_link(..., channel_id=None):
    payload = {
        "metadata": {
            "channel_id": channel_id,
            ...
        }
    }
    # Retorna também o channel_id
```

### 3. Webhook Processa Pagamento
```python
# Em: webhook_server.py
channel_id = get_payment_channel(payment_id)  # ← Busca ID do canal

channel = bot_instance.get_channel(channel_id)  # ← Pega objeto do canal

embed = discord.Embed(...)  # ← Cria embed com emojis

await channel.send(embed=embed)  # ← Envia no canal
```

## Troubleshooting

### Notificação não aparece no canal
- [ ] Verifique se `.env` tem um ID válido de canal (se necessário)
- [ ] Verifique se o bot tem permissão de enviar mensagens no canal
- [ ] Verifique se o webhook está recebendo as requisições (logs do Flask)

### Emojis não aparecem
- [ ] Confira a codificação do arquivo `.env` (deve ser UTF-8)
- [ ] Verifique se os emojis são válidos (teste no Discord)
- [ ] Reinicie o bot após alterar `.env`

### Erro "Channel not found"
- [ ] O canal foi deletado?
- [ ] O bot foi removido do servidor?
- [ ] Verifique o ID do canal com `!config_emojis`

## Funcionalidades Futuras

- [ ] Notificações configuráveis por servidor
- [ ] Canais separados para diferentes tipos de transação
- [ ] Mensagens editáveis com status em tempo real
- [ ] Reações automáticas (react role para confirmação)

## Resumo das Alterações

| Arquivo | Alteração |
|---------|-----------|
| `.env.example` | ✅ Adicionado 5 variáveis de emoji |
| `database.py` | ✅ Coluna `channel_id` na tabela payments |
| `cogs/payment.py` | ✅ Captura `ctx.channel.id` no `/cobrar` |
| `payment_handler.py` | ✅ Aceita e retorna `channel_id` |
| `webhook_server.py` | ✅ Envia notificação no canal com emojis |

---

**Versão:** 2.1  
**Data:** 2025  
**Tipo:** Nova Funcionalidade - Notificações em Canal com Emojis Personalizáveis
