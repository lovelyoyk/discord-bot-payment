# 🤖 Discord Payment Bot v3.0

Um bot Discord completo para gerenciamento de pagamentos via MisticPay com sistema de carteira, permissões por cargo, e transações seguras.

## ✨ Recursos Principais

### 💰 Sistema de Carteira
- **Saldo Pessoal**: Cada usuário tem seu próprio saldo
- **Histórico Detalhado**: Últimas 10 transações com datas
- **Dashboard**: Visualize `/meusdados` com saldo e transações
- **Saques**: Botão para sacar para PIX configurado

### 🔐 Sistema de Permissões
- **Owner Hardcoded**: IDs de dono definidos no `config.py`
- **Permissões por Cargo**: Admin controla quem pode cobrar
- **Comandos de Admin**: `/add-permissao`, `/rm-permissao`, `/listar-permissoes`

### 💳 Pagamentos Integrados
- **MisticPay**: Integração completa com webhooks
- **Notificações em Tempo Real**: Confirmação no canal + DM privada
- **Referência Única**: Cada pagamento tem um ID único do MisticPay
- **Reembolsos**: Sistema de reembolso integrado com MisticPay

### 🔒 Segurança
- **Anti-Race Conditions**: Funções com lock para múltiplos usuários simultâneos
- **Validação de Webhook**: HMAC-SHA256 para autenticação
- **Transações Atômicas**: BEGIN IMMEDIATE para isolamento de dados

---

## 📋 Comandos

### 👤 Comandos de Usuário

```
/saldo                          Ver saldo pessoal e últimas 10 transações
/meusdados                      Ver dados pessoais com opção de apagar
/pix <chave> <tipo>             Configurar chave PIX
/historico [limite]             Ver histórico completo de transações
```

### 💳 Comandos de Vendedor

```
/cobrar @usuario <valor> [sim]  Gerar cobrança com QR + botão de pagamento
/sacar [valor]                  Solicitar saque para PIX configurado
```

### 🔐 Comandos de Admin (Owner apenas)

```
/add-permissao @cargo           Permitir que cargo possa cobrar
/rm-permissao @cargo            Remover permissão de cargo
/listar-permissoes              Listar todos os cargos com permissão

/adicionarsaldo @user <valor>   Adicionar saldo manualmente
/removersaldo @user <valor>     Remover saldo manualmente
/reembolsar @user <valor> <motivo>  Reembolsar cliente
/listar-reembolsos              Listar reembolsos pendentes

/configurar-taxas <taxa>        Configurar taxa de transação
/saldo-geral                    Ver saldo total do servidor
/listar-usuarios                Listar todos os usuários registrados
```

---

## 🚀 Instalação Rápida

### 1. Clonar Repositório
```bash
git clone https://github.com/seu-usuario/discord-payment-bot.git
cd discord-payment-bot
```

### 2. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 3. Configurar Variáveis de Ambiente
Crie um arquivo `.env`:

```env
# Discord
DISCORD_BOT_TOKEN=seu_token_aqui
DISCORD_BOT_PREFIX=!

# MisticPay
MISTICPAY_API_KEY=sua_api_key
WEBHOOK_SECRET=seu_webhook_secret
WEBHOOK_URL=https://seu-dominio.com:5000/webhook

# Banco de Dados
DATABASE_PATH=./data/bot.db

# Owner IDs (edite também em config.py)
OWNER_ID=seu_discord_id

# Emojis (opcional)
EMOJI_SUCESSO=✅
EMOJI_CLIENTE=👥
EMOJI_VENDEDOR=👤
EMOJI_VALOR=💰
EMOJI_PAGAMENTO=💳
```

### 4. Atualizar config.py
```python
OWNER_IDS = [
    123456789,  # Seu ID do Discord
    987654321,  # Outro owner (opcional)
]
```

### 5. Executar Bot
```bash
python main.py
```

---

## 📊 Estrutura do Projeto

```
discord-payment-bot/
├── main.py                          # Arquivo principal do bot
├── config.py                        # Configuração de Owner IDs
├── database.py                      # Funções de banco de dados
├── payment_handler.py               # Integração com MisticPay
├── webhook_server.py                # Servidor Flask para webhooks
├── wallet_components.py             # Componentes de UI da carteira
├── requirements.txt                 # Dependências Python
├── .env.example                     # Exemplo de variáveis de ambiente
├── cogs/
│   ├── payment.py                   # Comandos de pagamento
│   ├── relatorios.py                # Comandos de relatório
│   └── admin.py                     # Comandos administrativos
├── data/
│   └── bot.db                       # Banco de dados SQLite
└── README.md                        # Este arquivo
```

---

## 🔗 Integração MisticPay

### Configuração Automática
O bot faz **automaticamente**:
- ✅ Recebe e valida pagamentos
- ✅ Atualiza saldos no banco de dados
- ✅ Envia notificações em tempo real
- ✅ Registra histórico detalhado
- ✅ Processa reembolsos

### Configuração Manual
Você precisa fazer:
1. Criar conta em https://misticpay.com
2. Gerar API Key e Webhook Secret
3. Configurar webhook no painel MisticPay
4. Atualizar `.env` com credenciais
5. Testar integração

**Veja [MISTICPAY_INTEGRATION_GUIDE.md](MISTICPAY_INTEGRATION_GUIDE.md) para detalhes completos.**

---

## 📊 Banco de Dados

### Tabelas Principais

| Tabela | Descrição |
|--------|-----------|
| `users` | Usuários com saldo e chave PIX |
| `transactions` | Histórico simples de transações |
| `transaction_history` | Histórico detalhado com referências |
| `payments` | Pagamentos MisticPay |
| `withdrawals` | Solicitações de saque |
| `cargo_permissions` | Cargos com permissão de cobrar |
| `refunds` | Reembolsos solicitados |

---

## 🔒 Segurança e Concorrência

### Proteção contra Race Conditions

O bot usa funções seguras de banco de dados:

```python
safe_add_balance()      # Adiciona saldo com lock
safe_remove_balance()   # Remove saldo com lock
safe_transfer_balance() # Transfere entre usuários com lock
safe_withdraw_balance() # Processa saque com lock
```

Cada operação usa `BEGIN IMMEDIATE` para garantir isolamento total de dados.

### Validação de Webhook

Todos os webhooks são validados com HMAC-SHA256:

```python
signature = hmac.new(
    WEBHOOK_SECRET.encode(),
    payload,
    hashlib.sha256
).hexdigest()
```

---

## 📈 Monitoramento

### Logs do Bot
```bash
tail -f bot.log
```

### Health Check
```bash
curl http://localhost:5000/health
```

### Verificar Lock Status
```python
from database import get_transaction_lock_status
print(get_transaction_lock_status())
```

---

## ❓ Troubleshooting

### Bot não conecta
- Verifique `DISCORD_BOT_TOKEN` em `.env`
- Verifique permissões do bot no Discord

### Webhook não recebe pagamentos
- Teste com `curl http://localhost:5000/health`
- Verifique `WEBHOOK_URL` no painel MisticPay
- Verifique `WEBHOOK_SECRET` corresponde

### Saldo não atualiza
- Verifique logs do bot (`python main.py`)
- Verifique BD não está corrompido
- Reprocesse manualmente com `/adicionarsaldo`

### Múltiplos saques simultâneos
- O lock evita isso automaticamente
- Verifique logs para timeout

---

## 📝 Changelog

### v3.0 - 2024
- ✨ Sistema de carteira completo
- ✨ Histórico detalhado de transações
- ✨ Anti-race conditions com lock
- ✨ Permissões por cargo
- ✨ Sistema de reembolso
- ✨ Dashboard de dados pessoais
- 🔧 Refactor completo de notificações
- 🔒 Validação segura de webhooks

### v2.1 - 2024
- 📦 Notificações de pagamento customizáveis
- 🎨 Emojis personalizáveis

### v2.0 - 2024
- 🚀 Integração MisticPay
- 💰 Sistema de saldo
- 💳 Cobrança com QR Code

---

## 📄 Licença

MIT License - Veja [LICENSE](LICENSE) para detalhes

---

## 🤝 Contribuindo

1. Fork o repositório
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

---

## 📞 Suporte

Para dúvidas ou reportar bugs:
1. Abra uma issue no GitHub
2. Consulte a documentação: [MISTICPAY_INTEGRATION_GUIDE.md](MISTICPAY_INTEGRATION_GUIDE.md)
3. Verifique os logs do bot

---

**Desenvolvido com ❤️ para a comunidade Discord**

Versão: 3.0 | Última atualização: 2024
