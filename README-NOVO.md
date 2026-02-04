# Bot de Pagamento Discord com MisticPay

Sistema completo de pagamentos para Discord com integração **MisticPay**, geração automática de QR Code, saques automáticos via PIX e saldos individuais por vendedor.

## 🎯 Características

✅ **Integração MisticPay** - Gateway de pagamento brasileira  
✅ **QR Code Automático** - Gerado em tempo real para cada cobrança  
✅ **Saldos Separados** - Cada vendedor tem seu próprio saldo  
✅ **Saques Automáticos** - PIX direto para a chave do vendedor  
✅ **Sistema de Roles** - Defina quem pode cobrar/sacar  
✅ **Webhook em Tempo Real** - Pagamentos creditados automaticamente  

## 🚀 Setup Rápido

### 1. Pré-requisitos

- Python 3.10+
- Conta MisticPay (https://misticpay.com)
- Bot Discord criado (https://discord.com/developers)

### 2. Instalação

```bash
git clone seu-repo
cd discord-bot-payment
pip install -r requirements.txt
```

### 3. Configurar Ambiente

Copie `.env.example` para `.env`:

```bash
cp .env.example .env
```

**Preencha as variáveis:**

```
# Bot Discord
DISCORD_BOT_TOKEN=seu_token_bot_discord
OWNER_ID=seu_id_discord

# MisticPay
MISTICPAY_API_KEY=sua_chave_api_misticpay
WEBHOOK_SECRET=seu_webhook_secret_misticpay

# Roles
VENDEDOR_ROLE_ID=id_do_role_vendedor

# Banco de dados
DATABASE_PATH=./data/bot.db

# Webhook
WEBHOOK_URL=https://seu-dominio.com/webhook
```

### 4. Configurar MisticPay

1. Acesse seu dashboard MisticPay
2. Crie uma aplicação/integração
3. Copie a **API Key**
4. Configure o webhook:
   - URL: `https://seu-dominio.com/webhook`
   - Events: `charge.paid`
5. Copie o **Webhook Secret**

### 5. Criar Role no Discord

1. Vá para Configurações do Servidor > Cargos
2. Crie um novo cargo chamado "Vendedor"
3. Copie o ID do cargo
4. Cole em `VENDEDOR_ROLE_ID` no `.env`

### 6. Executar

**Terminal 1 - Bot Discord:**

```bash
python main.py
```

**Terminal 2 - Webhook Server (em outro terminal):**

```bash
python webhook_server.py
```

## 📝 Comandos Disponíveis

### 🔑 Configuração

| Comando | Descrição |
|---------|-----------|
| `!pix <chave>` | Define sua chave PIX (CPF, Email, Telefone ou Chave aleatória) |

### 💰 Saldos (Público)

| Comando | Descrição |
|---------|-----------|
| `!saldo` | Ver seu saldo pessoal |
| `!saldo_geral` | Ver saldo total de todos |
| `!historico` | Ver suas transações |

### 💳 Pagamentos (Vendedores)

| Comando | Descrição |
|---------|-----------|
| `!cobrar <valor> [descricao]` | Gera link + QR Code para cobrar (ex: `!cobrar 50 Venda de Produto`) |
| `!sacar [valor]` | Saca para sua chave PIX (sem valor = saca tudo) |

### 🔐 Admin (Apenas Dono)

| Comando | Descrição |
|---------|-----------|
| `!adicionar_saldo <user_id> <valor>` | Adiciona saldo manualmente |
| `!remover_saldo <user_id> <valor>` | Remove saldo manualmente |
| `!listar_usuarios` | Lista top 20 usuários por saldo |
| `!dar_role_vendedor [@user]` | Concede role de vendedor |

## 🔄 Fluxo de Pagamento

```
1. Vendedor usa: !cobrar 50 "Produto XYZ"
   ↓
2. Bot gera link + QR Code MisticPay
   ↓
3. Cliente escaneia QR ou clica no link
   ↓
4. Cliente faz pagamento (PIX, Débito, Crédito)
   ↓
5. MisticPay notifica webhook
   ↓
6. Saldo é creditado AUTOMATICAMENTE no vendedor
   ↓
7. Vendedor usa: !sacar
   ↓
8. Dinheiro vai direto para a chave PIX do vendedor
```

## 🏗️ Estrutura do Projeto

```
discord-bot-payment/
├── main.py                 # Bot Discord principal
├── database.py             # SQLite (usuários, saldos, transações)
├── payment_handler.py      # Integração MisticPay + QR Code
├── webhook_server.py       # Flask webhook receiver
├── cogs/
│   └── payment.py         # Todos os comandos
├── requirements.txt        # Dependências
├── .env.example           # Template .env
├── README.md
└── data/
    └── bot.db            # Banco de dados SQLite
```

## 💾 Banco de Dados

### Tabelas

**users**
- `user_id` - ID do Discord
- `balance` - Saldo em R$
- `pix_key` - Chave PIX cadastrada

**transactions**
- Histórico de todas as operações (créditos/débitos)

**payments**
- Registro de pagamentos recebidos
- Status e ID MisticPay

**withdrawals**
- Histórico de saques processados

## 🔧 Customizações

### Mudar Comissão

Edite `payment_handler.py` para adicionar comissão:

```python
comissao = amount * 0.05  # 5% de comissão
saldo_vendedor = amount - comissao
```

### Diferentes Métodos de Pagamento

MisticPay suporta:
- ✅ PIX (instantâneo)
- ✅ Boleto (até 1 dia útil)
- ✅ Crédito (parcelado)
- ✅ Débito

Configure em seu dashboard MisticPay.

## 📱 Exemplo de Uso

```
Vendedor João: !pix 123.456.789-10
Bot: ✅ Chave PIX Salva

Vendedor João: !cobrar 100 "Consultoria"
Bot: [Envia link + QR Code em PNG]

Cliente: [Escaneia QR ou clica no link]
Cliente: [Faz pagamento de R$ 100]

Bot: ✅ Pagamento recebido para João!
João: !saldo
Bot: R$ 100.00

João: !sacar
Bot: R$ 100.00 será transferido para sua chave PIX
```

## 🐛 Troubleshooting

| Problema | Solução |
|----------|---------|
| Bot não conecta | Verifique `DISCORD_BOT_TOKEN` no `.env` |
| Webhook não recebe pagamentos | Confirme URL pública e `WEBHOOK_SECRET` |
| QR Code não aparece | Verifique instalação da biblioteca `qrcode` |
| Saldo não atualiza | Verifique logs do `webhook_server.py` |
| Role de vendedor não funciona | Certifique-se de ter configurado `VENDEDOR_ROLE_ID` |

## 📊 Checklist de Deploy

- [ ] Conta MisticPay ativa e verificada
- [ ] API Key e Webhook Secret copiados
- [ ] `.env` preenchido com todas as variáveis
- [ ] Role "Vendedor" criado no Discord
- [ ] Servidor com HTTPS + porta 5000 aberta
- [ ] Bot rodando em systemd ou PM2
- [ ] Webhook configurado em MisticPay

## 💡 Dicas

1. **Teste em modo sandbox** antes de usar em produção
2. **Faça backup do banco de dados** regularmente
3. **Configure logs** para rastrear problemas
4. **Use variáveis de ambiente** seguras em produção
5. **Monitore webhook** para garantir recebimento de pagamentos

## 🤝 Suporte

- MisticPay: https://misticpay.com/suporte
- Discord.py: https://discordpy.readthedocs.io
- Issues: Abra uma issue no repositório

## 📄 Licença

MIT License - Veja LICENSE.md
