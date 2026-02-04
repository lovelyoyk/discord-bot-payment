# 🤖 Bot de Pagamento Discord

Sistema completo e profissional de pagamentos para Discord com integração MisticPay (PIX), notificações em canal, gerenciamento de vendedores e saques automáticos.

## ✨ Funcionalidades Principais

- ✅ **Pagamentos com PIX** via MisticPay
- ✅ **QR Code automático** em cada cobrança
- ✅ **Notificações em canal** com emojis personalizáveis
- ✅ **Sistema de vendedores** com cargo configurável
- ✅ **Taxas flexíveis** (recebimento + saque)
- ✅ **Validação PIX** (CPF, Email, Telefone, Chave Aleatória)
- ✅ **Confirmação em 2 etapas** para saques (anti-erro)
- ✅ **Dashboard visual** com métricas em tempo real
- ✅ **Relatórios por período** (hoje/semana/mês)
- ✅ **Webhooks para pagamentos** em tempo real
- ✅ **Banco de dados SQLite** com histórico completo

## 🚀 Setup Rápido

### 1. Clonar o Repositório

```bash
git clone seu-repo
cd discord-bot-payment
```

### 2. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 3. Configurar Variáveis de Ambiente

```bash
cp .env.example .env
```

**Preencha as variáveis obrigatórias:**

```env
# Discord
DISCORD_BOT_TOKEN=seu_token_aqui
OWNER_ID=seu_id_discord

# MisticPay
MISTICPAY_API_KEY=sua_api_key_misticpay
WEBHOOK_SECRET=seu_secret_webhook

# Sistema
VENDEDOR_ROLE_ID=id_do_cargo_vendedor
TAXA_RECEBIMENTO=0.025  # 2.5%
TAXA_SAQUE=0.01         # 1%

# Emojis (opcional - pode usar os padrões)
EMOJI_SUCESSO=✅
EMOJI_CLIENTE=👥
EMOJI_VENDEDOR=👤
EMOJI_VALOR=💰
EMOJI_PAGAMENTO=💳
```

### 4. Obter IDs do Discord

Para obter seus IDs:

```
1. Ative Modo Desenvolvedor: Discord → User Settings → Advanced → Developer Mode
2. Seu ID: Clique com direito em você mesmo → Copy User ID
3. ID do Cargo: Clique com direito no cargo → Copy Role ID
4. ID do Canal: Clique com direito no canal → Copy Channel ID
```

### 5. Configurar MisticPay

1. Acesse https://misticpay.com
2. Crie uma conta e gere sua API Key
3. Configure webhook para: `https://seu-dominio.com/webhook`
4. Copie a API Key para `.env`

### 6. Executar

**Terminal 1 - Bot Discord:**

```bash
python main.py
```

**Terminal 2 - Webhook Server (em outro terminal):**

```bash
python webhook_server.py
```

> ⚠️ **Importante:** Ambos devem estar rodando simultaneamente

## 📋 Comandos Disponíveis

### 👤 Comandos de Usuário

| Comando | Descrição |
|---------|-----------|
| `!saldo` | Ver seu saldo pessoal |
| `!saldo_geral` | Ver saldo total do sistema |
| `!historico` | Ver suas transações recentes |
| `!pix <chave>` | Configurar sua chave PIX |
| `!cobrar @cliente <valor> [sim/nao]` | Criar cobrança com QR Code |
| `!sacar [valor]` | Sacar saldo (com confirmação) |
| `!dashboard` | Ver dashboard com métricas |

### 👨‍💼 Comandos de Vendedor

*(Requer cargo de vendedor)*

| Comando | Descrição |
|---------|-----------|
| `!adicionar_saldo @user <valor>` | Adicionar saldo manualmente |
| `!remover_saldo @user <valor>` | Remover saldo |
| `!listar_usuarios` | Listar todos usuários e saldos |
| `!config_taxas [receb] [saque]` | Configurar taxas |
| `!relatorio [hoje/semana/mes]` | Ver relatório de vendas |
| `!ranking` | Top 10 vendedores |

### 👑 Comandos do Owner

*(Apenas o dono do bot)*

| Comando | Descrição |
|---------|-----------|
| `!dar_role_vendedor @user` | Atribuir cargo de vendedor |
| `!config_emojis` | Ver emojis configurados |

## 💳 Fluxo de Pagamento Completo

```
┌─────────────────────────────────────────┐
│ 1. Vendedor usa: !cobrar @cliente 100   │
└────────────────┬────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│ 2. Bot gera:                            │
│    • Link MisticPay                     │
│    • QR Code em arquivo                 │
│    • Botão "Pagar Agora"                │
└────────────────┬────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│ 3. Cliente recebe DM com link           │
│    (ou escaneia QR)                     │
└────────────────┬────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│ 4. Cliente faz pagamento via PIX        │
└────────────────┬────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│ 5. Webhook MisticPay notifica bot       │
└────────────────┬────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│ 6. Bot envia notificação no CANAL       │
│    (onde foi criada a cobrança)         │
│                                         │
│    ✅ Pagamento Confirmado              │
│    👤 Vendedor: @VendedorX              │
│    💰 Valor: R$ 100,00                  │
│    💳 ID: pay_abc123                    │
└────────────────┬────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│ 7. Saldo adicionado automaticamente     │
│    + DM de confirmação ao vendedor      │
└─────────────────────────────────────────┘
```

## 🔔 Notificações em Canal

Uma das principais funcionalidades é que as notificações de pagamento aparecem **automaticamente no canal** onde o comando `/cobrar` foi executado!

### Exemplo de Notificação

```
✅ Pagamento Confirmado

👤 Vendedor: @João#1234
💰 Valor: R$ 250,00
💳 ID da Transação: pay_1234abcd5678efgh

Saldo foi creditado automaticamente
```

### Personalizar Emojis

Edite `.env` com seus emojis preferidos:

```env
# Tema Profissional
EMOJI_SUCESSO=☑️
EMOJI_CLIENTE=💼
EMOJI_VENDEDOR=👨‍💼
EMOJI_VALOR=💵
EMOJI_PAGAMENTO=🏦

# Tema Divertido
EMOJI_SUCESSO=🎉
EMOJI_CLIENTE=🤝
EMOJI_VENDEDOR=😎
EMOJI_VALOR=🤑
EMOJI_PAGAMENTO=🎁
```

> Para ver ajuda completa, consulte [NOTIFICACOES_CANAL.md](NOTIFICACOES_CANAL.md)

## 🔧 Estrutura do Projeto

```
discord-bot-payment/
├── main.py                          # Bot principal
├── database.py                      # SQLite gerenciador
├── payment_handler.py               # Integração MisticPay
├── webhook_server.py                # Servidor Flask webhook
├── validador_pix.py                 # Validação PIX
├── ui_components.py                 # Componentes Discord UI
├── migrate_payments_channel.py       # Script de migração
│
├── cogs/
│   ├── payment.py                   # Comandos de pagamento
│   └── relatorios.py                # Relatórios e dashboard
│
├── .env.example                     # Template de configuração
├── requirements.txt                 # Dependências Python
│
├── README.md                        # Este arquivo
├── NOTIFICACOES_CANAL.md            # Guia de notificações
├── CONFIGURACAO_TAXAS.md            # Guia de taxas
└── bot.db                           # Banco SQLite (criado automaticamente)
```

## 💾 Banco de Dados

### Tabelas SQLite

**Users:**
```sql
user_id (PRIMARY)
balance
pix_key
created_at
updated_at
```

**Transactions:**
```sql
id (PRIMARY)
user_id
type (deposit/withdrawal/payment)
amount
description
created_at
```

**Payments:**
```sql
payment_id (PRIMARY)
receiver_id
payer_id
amount
status
qr_code
misticpay_id
channel_id          ← Novo! Para notificações
created_at
```

**Withdrawals:**
```sql
id (PRIMARY)
user_id
amount
status
pix_key
created_at
processed_at
```

## 🚀 Migração de Banco Antigo

Se você tem um banco de dados existente sem a coluna `channel_id`, execute:

```bash
python migrate_payments_channel.py
```

Este script:
- ✅ Faz backup automático (`bot.db.backup_timestamp`)
- ✅ Adiciona coluna `channel_id` à tabela `payments`
- ✅ Verifica se a migração foi bem-sucedida

## 🌐 Deploy em Produção

### Opção 1: Railway (Recomendado)

```bash
# Instalar Railway CLI
npm i -g @railway/cli

# Fazer login
railway login

# Configurar projeto
railway init

# Fazer deploy
railway up
```

### Opção 2: Heroku

```bash
# Instalar Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

heroku login
heroku create seu-bot-nome
git push heroku main
```

### Opção 3: VPS Linux (DigitalOcean, AWS, etc)

```bash
# SSH no servidor
ssh root@seu-servidor.com

# Instalar Python
apt update && apt install -y python3.11 python3-pip

# Clonar e instalar
git clone seu-repo
cd discord-bot-payment
pip install -r requirements.txt

# Usar systemd para manter rodando
# (Ver guia completo em wiki)
```

**Requisitos:**
- Python 3.8+
- HTTPS obrigatório (para webhook)
- Firewall liberado para porta 5000
- Variáveis de ambiente configuradas

## 🐛 Troubleshooting

### Bot não conecta
```
❌ Erro: discord.errors.LoginFailure
✅ Solução: Verifique DISCORD_BOT_TOKEN no .env
```

### Webhook não recebe pagamentos
```
❌ Erro: 401 Unauthorized
✅ Solução: Confirme WEBHOOK_SECRET está correto
```

### Notificação não aparece no canal
```
❌ Erro: Channel not found
✅ Solução: 
  1. Verifique se canal ainda existe
  2. Confirme bot tem permissão de enviar mensagens
  3. Veja logs do webhook_server.py
```

### Erro ao sacar
```
❌ Erro: Invalid PIX key
✅ Solução: Use !pix <chave> para configurar corretamente
```

## 📚 Documentação Adicional

- [NOTIFICACOES_CANAL.md](NOTIFICACOES_CANAL.md) - Guia completo de notificações
- [CONFIGURACAO_TAXAS.md](CONFIGURACAO_TAXAS.md) - Configurar taxas de recebimento e saque
- [GUIA_COBRAR.md](GUIA_COBRAR.md) - Tutorial do comando cobrar
- [SISTEMA_COMPLETO.md](SISTEMA_COMPLETO.md) - Visão geral de toda a arquitetura

## 🤝 Contribuindo

Sugestões e melhorias são bem-vindas! Abra uma issue ou faça um pull request.

## 📄 Licença

MIT License - Veja LICENSE.md para detalhes

## 🆘 Suporte

Está tendo problemas? 

1. Verifique [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Consulte os logs: `python main.py 2>&1 | tee bot.log`
3. Abra uma issue no repositório

---

**Versão:** 2.1  
**Última Atualização:** 2025  
**Status:** ✅ Produção-Ready
