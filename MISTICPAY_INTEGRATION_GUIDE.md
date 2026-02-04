# 🔗 Guia de Integração MisticPay

Este documento explica como integrar o bot de pagamento com a plataforma **MisticPay** para receber e processar pagamentos automaticamente.

## 📋 Índice

1. [O que é Automático](#automático)
2. [O que é Manual](#manual)
3. [Configuração Passo a Passo](#configuração-passo-a-passo)
4. [Testando a Integração](#testando-a-integração)
5. [Troubleshooting](#troubleshooting)

---

## ✅ O que é Automático

O bot faz **automaticamente** as seguintes ações quando um pagamento é confirmado:

### 1. **Recebimento de Pagamentos**
- ✅ Recebe notificações do webhook MisticPay
- ✅ Valida a assinatura da requisição
- ✅ Extrai dados do pagamento (ID, valor, referência)
- ✅ Adiciona saldo ao vendedor no banco de dados

### 2. **Histórico de Transações**
- ✅ Registra cada transação com:
  - ID único do MisticPay
  - Referência (ref) da transação
  - Valor bruto e líquido
  - Tipo de transação (payment, refund, etc)
  - Data/hora da transação
  - Status

### 3. **Notificações no Discord**
- ✅ Envia mensagem no canal original da cobrança
- ✅ Envia DM privada ao vendedor
- ✅ Inclui:
  - `:emoji: Venda Aprovada!`
  - Valor em Reais (R$)
  - ID da cobrança
  - Referência do MisticPay
  - Nome do cliente e vendedor

### 4. **Reembolsos Automáticos**
- ✅ Processa reembolsos via `/reembolsar` command
- ✅ Integra com MisticPay API para enviar reembolso
- ✅ Atualiza saldo do cliente
- ✅ Registra motivo do reembolso

---

## 🔧 O que é Manual

Você **precisa fazer manualmente** as seguintes configurações:

### 1. **Criar Conta MisticPay**
- Acesse: https://misticpay.com
- Crie uma conta de negócio
- Complete o processo KYC/verificação

### 2. **Gerar Chaves de API**
- No painel MisticPay, vá para: **Configurações > API**
- Gere uma **API Key** (para autenticação)
- Copie o **Webhook Secret** (para validar webhooks)

### 3. **Configurar Variáveis de Ambiente**
Edite seu arquivo `.env` e adicione:

```env
# MisticPay Configuration
MISTICPAY_API_KEY=sua_api_key_aqui
MISTICPAY_API_URL=https://api.misticpay.com
WEBHOOK_SECRET=seu_webhook_secret_aqui
WEBHOOK_URL=https://seu-dominio.com:5000/webhook

# Emojis para Notificações (opcional)
EMOJI_SUCESSO= <a:check_yes:1429518156136972400>  
EMOJI_CLIENTE= <:member:1461081150566043884>
EMOJI_VENDEDOR= <:SUPORTE:1461101196407214175>
EMOJI_VALOR= <:dinheiro1:1461111258676859056>
EMOJI_PAGAMENTO= <a:am_rd_spc:1461222342360305797>
```

### 4. **Configurar Webhook no Painel MisticPay**
- Acesse o painel MisticPay
- Vá para: **Webhooks > Adicionar Webhook**
- Configure:
  - **URL**: `https://seu-dominio.com:5000/webhook`
  - **Eventos**: `payment.confirmed`, `payment.failed`, `refund.processed`
  - **Secret**: Cole o valor do `WEBHOOK_SECRET`

### 5. **Configurar Seu Domínio**
Se estiver testando localmente, você precisa:
- Usar um serviço como **ngrok** para expor a porta 5000
- Exemplo: `ngrok http 5000`
- Será gerado um URL como: `https://abc123.ngrok.io`
- Use este URL no webhook do MisticPay

Para **produção**:
- Configure um domínio (exemplo: `payments.seudominio.com`)
- Configure SSL/HTTPS (recomendado: Let's Encrypt)
- Aponte o domínio para seu servidor

### 6. **Definir Owner IDs**
No arquivo `config.py`, adicione os IDs dos donos do bot:

```python
OWNER_IDS = [
    123456789,  # ID do Discord do Dono 1
    987654321,  # ID do Discord do Dono 2
]
```

Para encontrar seu ID do Discord:
1. Ative modo desenvolvedor no Discord
2. Clique com botão direito em você mesmo
3. Selecione "Copiar ID de Usuário"

### 7. **Configurar Permissões de Cargo**
Os donos podem adicionar cargos permissões para cobrar:

```
/add-permissao @vendedor
/rm-permissao @vendedor
/listar-permissoes
```

---

## 🚀 Configuração Passo a Passo

### Passo 1: Instalar Dependências
```bash
pip install -r requirements.txt
```

Certifique-se que tem:
- `discord.py`
- `flask`
- `flask-cors`
- `python-dotenv`

### Passo 2: Preparar MisticPay
1. Crie conta em https://misticpay.com
2. Copie API Key e Webhook Secret
3. Atualize `.env`

### Passo 3: Configurar Bot
1. Edite `config.py` com seus OWNER_IDs
2. Adicione permissões de cargo:
   ```
   /add-permissao @Vendedores
   ```

### Passo 4: Iniciar o Bot
```bash
python main.py
```

Você verá:
```
✅ Bot conectado como SeuBot#1234
✅ Cog carregado: payment.py
✅ Cog carregado: admin.py
✅ Webhook rodando em 0.0.0.0:5000
```

### Passo 5: Testar
1. Execute um comando de teste:
   ```
   /saldo
   ```
2. Crie uma cobrança de teste:
   ```
   /cobrar @usuario 10
   ```

---

## 🧪 Testando a Integração

### Teste 1: Webhook Health Check
```bash
curl http://localhost:5000/health
```

Resposta esperada:
```json
{"status": "online", "service": "MisticPay Webhook"}
```

### Teste 2: Simular Pagamento
Use a API MisticPay para criar um pagamento de teste:

```bash
curl -X POST https://api.misticpay.com/v1/charges \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 10.00,
    "description": "Teste de integração",
    "type": "pix",
    "payer_phone": "11999999999"
  }'
```

### Teste 3: Verificar Webhook
O webhook enviará dados para `http://localhost:5000/webhook` quando um pagamento for confirmado.

Monitore os logs do bot:
```
INFO: Recebido webhook de pagamento
INFO: Adicionado R$ 10.00 ao usuário #123456789
INFO: Notificação enviada no Discord
```

---

## 🔍 Troubleshooting

### ❌ Erro: "Webhook Secret inválido"
**Causa**: O secret no `.env` não corresponde ao MisticPay

**Solução**:
1. Vá ao painel MisticPay
2. Copie exatamente o Webhook Secret
3. Cole em `.env` como `WEBHOOK_SECRET`
4. Reinicie o bot

### ❌ Erro: "Conexão recusada ao webhook"
**Causa**: O domínio/porta não está acessível

**Solução**:
- Local: Use `ngrok http 5000`
- Produção: Configure firewall/DNS corretamente
- Verifique porta 5000 está aberta

### ❌ Pagamento recebido mas saldo não atualizou
**Causa**: Possível erro no processamento do webhook

**Solução**:
1. Verifique logs do bot
2. Verifique status do webhook no painel MisticPay
3. Reprocesse manualmente via `/adicionarsaldo`

### ❌ Erro: "API Key inválida"
**Causa**: A chave de API está incorreta ou expirou

**Solução**:
1. Vá ao painel MisticPay
2. Gere uma nova API Key
3. Atualize em `.env`
4. Reinicie o bot

### ❌ Não estou recebendo notificações no Discord
**Causa**: Bot sem permissão no canal ou configuração incorreta

**Solução**:
1. Verifique se bot tem permissão "Enviar Mensagens" no canal
2. Verifique channel_id no banco de dados
3. Verifique logs do webhook

---

## 📊 Monitoramento

### Verificar Transações
```
/saldo
```
Mostra seu saldo e últimas 10 transações

### Listar Todos os Reembolsos
```
/listar-reembolsos
```
(Apenas donos)

### Ver Dados Pessoais
```
/meusdados
```
Mostra nome, email, CPX, chave PIX registrada, saldo e transações

---

## 🔐 Segurança

✅ **O que está seguro:**
- Webhooks validados com HMAC-SHA256
- IDs de dono hardcoded (não removem via bot)
- Senhas de API protegidas em `.env`
- Transações imutáveis no banco de dados

⚠️ **Melhorias Recomendadas:**
- Usar um `.env` criptografado em produção
- Fazer backup regular do banco de dados
- Monitorar logs de webhook
- Implementar 2FA no painel MisticPay

---

## 📚 Documentação Adicional

- [Documentação MisticPay](https://docs.misticpay.com)
- [Discord.py Docs](https://discordpy.readthedocs.io)
- [Flask Docs](https://flask.palletsprojects.com)

---

## ❓ Dúvidas?

Se tiver dúvidas sobre a integração:
1. Verifique os logs do bot (`python main.py`)
2. Consulte a documentação MisticPay
3. Abra uma issue no repositório

---

**Última atualização:** 2024
**Versão do bot:** v3.0
