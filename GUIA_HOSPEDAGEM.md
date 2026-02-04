# 🌐 Guia de Hospedagem do Bot Discord com Webhook

## ✅ Mudanças Recentes
- `/cobrar` agora usa parâmetro `valor` (mais intuitivo em português)
- Webhook server iniciando automaticamente na porta 5000
- Sistema de confirmação de pagamento funcionando

---

## 🚀 Opções de Hospedagem

### 1️⃣ **VPS Recomendada** (Melhor opção)

#### 🇧🇷 Provedores Brasileiros (Pagamento em R$):
- **Hostinger Brasil** - A partir de R$ 19,99/mês (aceita PIX, boleto, cartão)
  - 1 vCore, 1GB RAM, 50GB SSD
  - Datacenter em São Paulo
  - Suporte em português
  - Link: https://www.hostinger.com.br/vps-hospedagem

- **Contabo Brasil** - A partir de R$ 24,99/mês (PIX, boleto, cartão)
  - 4 vCores, 6GB RAM, 100GB SSD
  - Datacenter em São Paulo (latência baixa)
  - Melhor custo-benefício
  - Link: https://contabo.com/pt/

- **HostGator Brasil** - A partir de R$ 34,99/mês (PIX, boleto, cartão)
  - 2 vCores, 2GB RAM, 120GB SSD
  - Suporte 24/7 em português
  - Link: https://www.hostgator.com.br/servidor-vps

- **KingHost** - A partir de R$ 59,90/mês (PIX, boleto, cartão)
  - 1 vCore, 1GB RAM, 30GB SSD
  - 100% brasileiro, suporte premium
  - Link: https://king.host/vps-linux

- **Locaweb Cloud** - A partir de R$ 89,00/mês (PIX, boleto, cartão)
  - 1 vCore, 1GB RAM, 20GB SSD
  - Maior empresa brasileira de hospedagem
  - Link: https://www.locaweb.com.br/cloud/

#### 🌍 Provedores Internacionais (Pagamento em USD/EUR):
- **Contabo VPS** - A partir de €4.50/mês (mais barato)
- **DigitalOcean Droplet** - A partir de $6/mês (mais fácil)
- **AWS Lightsail** - A partir de $5/mês (bom uptime)
- **Oracle Cloud** - FREE TIER PERMANENTE (4 ARM CPUs, 24GB RAM)

#### 🏆 **Recomendação TOP:**
1. **Grátis:** Oracle Cloud (sempre grátis, mas precisa cartão internacional)
2. **Pago Brasil:** Contabo Brasil (R$ 24,99 - melhor custo-benefício)
3. **Suporte BR:** HostGator Brasil (R$ 34,99 - suporte em PT-BR)

#### Setup Recomendado Oracle Cloud (GRÁTIS):
```bash
# 1. Criar conta Oracle Cloud (sempre grátis)
# 2. Criar VM Instance Ubuntu 22.04 (ARM ou x86)
# 3. Conectar via SSH

# Instalar Python 3.11+
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip nginx certbot python3-certbot-nginx -y

# Clonar seu repositório
cd /opt
git clone <seu-repositorio>
cd discord-bot-payment

# Criar ambiente virtual
python3.11 -m venv .venv
source .venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Configurar .env
nano .env
# Cole suas configurações aqui
```

---

### 2️⃣ **Configurar Domínio + HTTPS**

Como você já tem domínio, vamos configurá-lo:

#### Passo 1: Apontar Domínio
No painel do seu provedor de domínio (GoDaddy, Hostinger, etc):

```dns
Tipo    Nome              Valor                    TTL
A       bot               <IP-DO-SERVIDOR>         600
A       webhook           <IP-DO-SERVIDOR>         600
```

Exemplos de URLs finais:
- `https://webhook.seudominio.com` - Para webhook MisticPay
- `https://bot.seudominio.com` - Dashboard/painel admin (futuro)

#### Passo 2: Configurar Nginx (Reverse Proxy)

```bash
sudo nano /etc/nginx/sites-available/webhook
```

Cole este conteúdo:

```nginx
server {
    listen 80;
    server_name webhook.seudominio.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Ativar site:
```bash
sudo ln -s /etc/nginx/sites-available/webhook /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### Passo 3: Adicionar SSL (HTTPS Grátis)

```bash
sudo certbot --nginx -d webhook.seudominio.com
# Escolha opção 2 (redirect HTTP -> HTTPS)
```

Renovação automática:
```bash
sudo certbot renew --dry-run  # Testar
```

---

### 3️⃣ **Rodar Bot como Serviço (systemd)**

Crie arquivo de serviço:

```bash
sudo nano /etc/systemd/system/discord-bot.service
```

Cole:

```ini
[Unit]
Description=Discord Bot Payment
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/discord-bot-payment
Environment="PATH=/opt/discord-bot-payment/.venv/bin"
ExecStart=/opt/discord-bot-payment/.venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Ativar e iniciar:

```bash
sudo systemctl daemon-reload
sudo systemctl enable discord-bot
sudo systemctl start discord-bot

# Ver logs
sudo journalctl -u discord-bot -f
```

---

### 4️⃣ **Configurar Webhook no MisticPay**

1. Acesse painel MisticPay
2. Vá em **Configurações > Webhooks**
3. Cole a URL: `https://webhook.seudominio.com/webhook`
4. Copie o `WEBHOOK_SECRET` gerado
5. Adicione no `.env`:

```env
WEBHOOK_SECRET=seu_secret_aqui
```

6. **IMPORTANTE:** Reiniciar bot após isso:
```bash
sudo systemctl restart discord-bot
```

---

### 5️⃣ **Firewall & Segurança**

#### Configurar UFW (Ubuntu Firewall):

```bash
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw enable
sudo ufw status
```

#### Fechar porta 5000 (só nginx acessa):
```bash
# NÃO fazer: sudo ufw allow 5000
# Bot roda em 127.0.0.1:5000 (só local)
# Nginx encaminha requisições HTTPS
```

---

## 📋 Checklist de Deploy

- [ ] VPS criada e rodando
- [ ] Python 3.11+ instalado
- [ ] Repositório clonado
- [ ] `.env` configurado
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Bot roda manualmente (`python main.py`)
- [ ] Domínio apontado para IP do servidor
- [ ] Nginx instalado e configurado
- [ ] SSL/HTTPS configurado (certbot)
- [ ] Serviço systemd criado
- [ ] Bot rodando como serviço
- [ ] Webhook URL configurada no MisticPay
- [ ] Firewall configurado
- [ ] Teste de pagamento realizado

---

## 🧪 Testar Webhook

### Teste Local (antes de deploy):

```bash
# Terminal 1 - Rodar bot
python main.py

# Terminal 2 - Simular webhook
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "event": "transaction.paid",
    "data": {
      "transactionId": "test_123",
      "amount": 10.50
    }
  }'
```

### Teste Produção (após deploy):

```bash
curl -X POST https://webhook.seudominio.com/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "event": "transaction.paid",
    "data": {
      "transactionId": "test_456",
      "amount": 25.00
    }
  }'
```

---

## 🔍 Monitoramento

### Ver logs do bot:
```bash
sudo journalctl -u discord-bot -f --lines=100
```

### Ver logs do Nginx:
```bash
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### Verificar status:
```bash
sudo systemctl status discord-bot
sudo systemctl status nginx
```

---

## 🆘 Troubleshooting

### Bot não inicia:
```bash
# Ver erro completo
sudo journalctl -u discord-bot -n 50

# Testar manualmente
cd /opt/discord-bot-payment
source .venv/bin/activate
python main.py
```

### Webhook não recebe:
```bash
# 1. Verificar se porta 5000 está ouvindo
sudo netstat -tlnp | grep 5000

# 2. Testar localmente
curl http://localhost:5000/health

# 3. Verificar Nginx
sudo nginx -t
curl https://webhook.seudominio.com/health
```

### SSL não funciona:
```bash
# Renovar certificado
sudo certbot renew --force-renewal

# Ver certificados
sudo certbot certificates
```

---

## 💡 Dicas Extras

### Backup Automático:
O bot já faz backup do database a cada 6 horas, mas você pode configurar backup na nuvem:

```bash
# Instalar rclone
curl https://rclone.org/install.sh | sudo bash

# Configurar Google Drive ou Dropbox
rclone config

# Script de backup
cat > /opt/backup.sh << 'EOF'
#!/bin/bash
cd /opt/discord-bot-payment
rclone copy database.db gdrive:bot-backups/
rclone copy logs/ gdrive:bot-backups/logs/
EOF

chmod +x /opt/backup.sh

# Adicionar ao cron (todo dia às 4h)
echo "0 4 * * * /opt/backup.sh" | sudo crontab -
```

### Atualizar Bot:
```bash
cd /opt/discord-bot-payment
git pull
source .venv/bin/activate
pip install -r requirements.txt --upgrade
sudo systemctl restart discord-bot
```

---

## 📊 Resumo de URLs

Após configuração completa:

| Serviço | URL |
|---------|-----|
| **Webhook MisticPay** | `https://webhook.seudominio.com/webhook` |
| **Health Check** | `https://webhook.seudominio.com/health` |
| **Bot Discord** | Conectado via Discord API |
| **SSH Server** | `ssh ubuntu@seudominio.com` |

---

## 🎯 Próximos Passos

Após hospedagem funcionando:

1. ✅ Re-ativar validação de webhook (remover comentário em webhook_server.py linha 54)
2. ✅ Implementar painel web administrativo
3. ✅ Adicionar monitoramento com Grafana/Prometheus
4. ✅ Configurar alertas por e-mail/Telegram
5. ✅ Adicionar testes automatizados

---

**Versão:** v3.2  
**Data:** 04/02/2026  
**Mudanças:** Parâmetro `valor` no /cobrar, webhook automático, guia completo de hospedagem
