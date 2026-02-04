# 📋 Checklist de Configuração v3.0

Use este checklist para garantir que tudo está configurado corretamente antes de usar o bot.

---

## ✅ Passo 1: Preparação Inicial

- [ ] Python 3.8+ instalado
- [ ] Git instalado
- [ ] Clone do repositório feito
- [ ] Dependências instaladas: `pip install -r requirements.txt`

---

## ✅ Passo 2: Configurar Discord

### Criar Bot no Discord Developer Portal

- [ ] Acesse https://discord.com/developers/applications
- [ ] Clique em "New Application"
- [ ] Nomeie como "Discord Payment Bot"
- [ ] Vá para "Bot" > "Add Bot"
- [ ] Copie o TOKEN (guarde com segurança!)
- [ ] Ative as intents:
  - [ ] `PRESENCE INTENT`
  - [ ] `SERVER MEMBERS INTENT`
  - [ ] `MESSAGE CONTENT INTENT`

### Adicionar Bot ao Servidor

- [ ] Vá para "OAuth2" > "URL Generator"
- [ ] Selecione scopes: `bot`
- [ ] Selecione permissões:
  - [ ] `Send Messages`
  - [ ] `Embed Links`
  - [ ] `Attach Files`
  - [ ] `Use Application Commands`
- [ ] Copie a URL gerada
- [ ] Abra em novo navegador
- [ ] Selecione seu servidor
- [ ] Autorize o bot

### Encontrar seu ID do Discord

- [ ] Ative "Developer Mode" em Configurações do Discord
- [ ] Clique com botão direito em você mesmo
- [ ] Selecione "Copy User ID"
- [ ] Guarde este número

---

## ✅ Passo 3: Configurar MisticPay

### Criar Conta

- [ ] Acesse https://misticpay.com
- [ ] Crie uma conta de negócio
- [ ] Complete verificação KYC (pode levar 24h)

### Gerar Credenciais

- [ ] No painel MisticPay, vá para **Configurações > API**
- [ ] Gere uma **API Key** (copie e guarde)
- [ ] Copie o **Webhook Secret** (guarde com segurança)
- [ ] Anote a **API URL** (geralmente `https://api.misticpay.com`)

### Configurar Webhook

- [ ] No painel MisticPay, vá para **Webhooks > Adicionar Webhook**
- [ ] Configure:
  - [ ] **URL**: `https://seu-dominio.com:5000/webhook`
  - [ ] **Eventos**: `payment.confirmed`, `payment.failed`, `refund.processed`
  - [ ] **Secret**: Cole o `WEBHOOK_SECRET` gerado

**Nota Local (Testes):**
- [ ] Baixe ngrok: https://ngrok.com/download
- [ ] Execute: `ngrok http 5000`
- [ ] Use a URL gerada (exemplo: `https://abc123.ngrok.io:5000/webhook`)

---

## ✅ Passo 4: Configurar Variáveis de Ambiente

### Criar arquivo `.env`

```bash
# Copie este template e preencha os valores
cp .env.example .env
```

### Preencher `.env`

```env
# Discord
DISCORD_BOT_TOKEN=xyz...  # Copie do Developer Portal

# MisticPay
MISTICPAY_API_KEY=api_key_aqui
WEBHOOK_SECRET=secret_aqui
WEBHOOK_URL=https://seu-dominio.com:5000/webhook
MISTICPAY_API_URL=https://api.misticpay.com

# Banco de Dados
DATABASE_PATH=./data/bot.db

# Owner (seu ID do Discord)
OWNER_ID=seu_id_aqui

# Emojis (opcional - customize)
EMOJI_SUCESSO=✅
EMOJI_CLIENTE=👥
EMOJI_VENDEDOR=👤
EMOJI_VALOR=💰
EMOJI_PAGAMENTO=💳
```

- [ ] Preencheu todos os campos
- [ ] Salvou o arquivo `.env`
- [ ] NÃO fez commit do `.env` (está no `.gitignore`)

---

## ✅ Passo 5: Configurar `config.py`

### Editar Owner IDs

```python
# Abra config.py e edite:

OWNER_IDS = [
    123456789,  # Seu ID do Discord
    987654321,  # Outro owner (opcional)
]
```

- [ ] Editou `config.py`
- [ ] Adicionou seu ID do Discord
- [ ] Salvou o arquivo

---

## ✅ Passo 6: Inicializar Banco de Dados

### Executar Teste

```bash
python test_v3.py
```

Você deve ver:
```
✅ Testes Completos para v3.0:
✅ TODOS OS TESTES PASSARAM COM SUCESSO!
```

- [ ] Teste executado sem erros
- [ ] Banco de dados criado em `./data/bot.db`
- [ ] Todas as tabelas iniciadas

---

## ✅ Passo 7: Executar o Bot

### Terminal 1 - Bot Discord

```bash
python main.py
```

Você deve ver:
```
✅ Bot conectado como SeuBot#1234
✅ Cog carregado: payment.py
✅ Cog carregado: admin.py
```

- [ ] Bot conectou com sucesso
- [ ] Todos os cogs carregados
- [ ] Sem erros nos logs

---

## ✅ Passo 8: Testar Comandos

### Teste 1: Verificar Bot Online

No Discord, execute:
```
/saldo
```

Você deve ver seu saldo (0 no início).

- [ ] Comando `/saldo` funcionou

### Teste 2: Configurar Cargo com Permissão

Como OWNER, execute:
```
/add-permissao @Vendedores
```

Você deve ver uma mensagem de sucesso.

- [ ] Permissão adicionada com sucesso

### Teste 3: Ver Dados Pessoais

Execute:
```
/meusdados
```

Você deve ver um embed com seus dados e botões.

- [ ] Dashboard de carteira exibido
- [ ] Botões aparecem (Sacar, Apagar Dados, Cancelar)

### Teste 4: Admin - Adicionar Saldo

Como OWNER, execute:
```
/adicionarsaldo @seu_nome 100
```

Você deve ver saldo aumentado em `/saldo`.

- [ ] Saldo adicionado manualmente
- [ ] Visualiza em `/saldo`

---

## ✅ Passo 9: Testar Integração MisticPay

### Health Check

```bash
curl http://localhost:5000/health
```

Resposta esperada:
```json
{"status": "online", "service": "MisticPay Webhook"}
```

- [ ] Webhook está online

### Simular Pagamento (Opcional)

Se MisticPay oferece modo teste, crie um pagamento de teste e verifique:
- [ ] Saldo foi atualizado
- [ ] Notificação apareceu no Discord
- [ ] Histórico foi registrado

---

## 🚨 Troubleshooting

### Bot não conecta
```
❌ Erro: Discord token inválido
✅ Solução: Verifique DISCORD_BOT_TOKEN em .env
```

- [ ] Token está correto
- [ ] Não há espaços extras
- [ ] Bot está habilitado no Developer Portal

### Webhook não recebe pagamentos
```
❌ Erro: Webhook connection refused
✅ Solução: Verifique WEBHOOK_URL em .env
```

- [ ] URL é pública (não localhost)
- [ ] Porta 5000 está aberta no firewall
- [ ] Usando ngrok localmente? URL atualizada?

### Saldo não atualiza
```
❌ Erro: Saldo continua 0 após pagamento
✅ Solução: Verifique MisticPay webhook
```

- [ ] Webhook configurado no painel MisticPay
- [ ] WEBHOOK_SECRET corresponde
- [ ] Verifique logs do bot (`python main.py`)

### Erro de banco de dados
```
❌ Erro: database locked
✅ Solução: Verifique race conditions
```

- [ ] Apenas uma instância do bot rodando
- [ ] Não acesse `bot.db` diretamente enquanto bot roda
- [ ] Reinicie o bot se travar

---

## 📊 Verificação Final

Você está pronto quando:

- [x] Bot conecta ao Discord
- [x] Todos os comandos `/` funcionam
- [x] Permissões de cargo funcionam
- [x] Dados pessoais exibem corretamente
- [x] Admin pode adicionar saldo
- [x] Histórico registra transações
- [x] Webhook está online

---

## 📚 Documentação Importante

Antes de usar em produção, leia:

1. **[README.md](README.md)** - Visão geral do bot
2. **[MISTICPAY_INTEGRATION_GUIDE.md](MISTICPAY_INTEGRATION_GUIDE.md)** - Setup detalhado
3. **[CHANGELOG_V3.md](CHANGELOG_V3.md)** - Mudanças implementadas

---

## 🎓 Dicas Importantes

### Segurança
- ⚠️ **NUNCA** commit o `.env` com credenciais reais
- ⚠️ **NUNCA** compartilhe seu `DISCORD_BOT_TOKEN`
- ⚠️ **NUNCA** compartilhe seu `MISTICPAY_API_KEY`
- 🔒 Use variáveis de ambiente em produção
- 🔒 Configure `.env` em `.gitignore` (já está configurado)

### Performance
- 💡 O lock de threading só funciona em uma instância
- 💡 Para múltiplas instâncias, use Redis ou semáforo distribuído
- 💡 Histórico limitado a 10 transações para performance

### Backup
- 📦 Faça backup regular de `data/bot.db`
- 📦 Guarde `.env` em local seguro
- 📦 Documente seus OWNER_IDs

---

## ❓ Ainda com Dúvidas?

1. Verifique o [MISTICPAY_INTEGRATION_GUIDE.md](MISTICPAY_INTEGRATION_GUIDE.md)
2. Verifique os logs do bot (`python main.py`)
3. Execute `python test_v3.py` para diagnóstico
4. Teste health check: `curl http://localhost:5000/health`

---

**Versão:** 3.0  
**Data:** 2024  
**Status:** Pronto para usar!

Quando terminar este checklist, você está pronto para usar o bot em produção! 🚀
