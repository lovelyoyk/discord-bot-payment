# 📋 Guia de Configuração - Sistema de Taxas e Cargos

## 🎯 Sistema de Cargo Único

O bot agora usa **UM ÚNICO CARGO** para todos os vendedores. Qualquer pessoa com este cargo pode:
- ✅ Usar `/cobrar` para gerar links de pagamento
- ✅ Usar `/sacar` para receber dinheiro
- ✅ Ver seu saldo pessoal

### Como Configurar

1. **Crie um cargo no Discord:**
   - Vá para: Configurações do Servidor > Cargos
   - Clique em "+" > Novo Cargo
   - Nome: `Vendedor` (ou o nome que quiser)
   - Cores (opcional)

2. **Copie o ID do cargo:**
   - Ative Modo de Desenvolvedor (User Settings > Advanced > Developer Mode)
   - Clique com direito no cargo > Copiar ID

3. **Configure no `.env`:**
   ```
   VENDEDOR_ROLE_ID=ID_QUE_COPIOU
   ```

4. **Dê o cargo a vendedores:**
   - Use: `!dar_role_vendedor @usuario`
   - Ou manualmente: Clique no usuário > Adicionar cargo

---

## 💸 Sistema de Taxas Flexível

### Tipos de Taxa

| Taxa | O que é? | Exemplo |
|------|----------|---------|
| **Taxa de Recebimento** | Cobrada do cliente | Se cliente paga R$ 100 e taxa é 2.5%, o cliente paga R$ 102,50 |
| **Taxa de Saque** | Cobrada do vendedor | Se vendedor tira R$ 100 e taxa é 1%, ele recebe R$ 99,00 |

### Configurar Taxas

#### Via Comando (Dinâmico)
```bash
!config_taxas 0.025 0.01
```
- `0.025` = 2.5% de taxa de recebimento
- `0.01` = 1% de taxa de saque

#### Via .env (Permanente)
Edite o `.env`:
```
TAXA_RECEBIMENTO=0.025
TAXA_SAQUE=0.01
```

---

## 📊 Como as Taxas Aparecem

### Comando `/cobrar` (cliente paga taxa)
```
💳 Cobrança de Serviço
Fatura gerada para @seu_nome

📋 Serviço
R$ 1,00

📊 Taxas
+ R$ 0,65 (Taxa 2.5%)

💰 Total
R$ 1,65

👤 Vendedor: seu_nome
```

**O cliente paga R$ 1,65 total.**
**Você recebe R$ 1,65 no saldo.**

### Comando `/sacar` (você paga taxa)
```
✅ Saque Processado

💰 Valor Sacado
R$ 100,00

📊 Taxa de Saque
- R$ 1,00 (1%)

💸 Você Receberá
R$ 99,00
```

**Você tinha R$ 100,00.**
**Você recebe R$ 99,00 no PIX.**

---

## 🔄 Fluxo Completo

```
1. Vendedor: !cobrar 50 "Consultoria"
   ↓
2. Bot calcula: 50 + (50 × 0.025) = R$ 51,25 (total para cliente)
   ↓
3. Cliente escaneia QR ou clica link
   ↓
4. Cliente paga R$ 51,25
   ↓
5. Webhook confirma pagamento
   ↓
6. Saldo vendedor + R$ 51,25 (automático)
   ↓
7. Vendedor: !sacar
   ↓
8. Bot calcula: 51,25 - (51,25 × 0.01) = R$ 50,74 (para PIX)
   ↓
9. Dinheiro vai para PIX do vendedor
```

---

## ⚙️ Exemplos de Configuração

### Opção 1: Sem taxas (Grátis)
```
TAXA_RECEBIMENTO=0
TAXA_SAQUE=0
```

### Opção 2: Padrão (Recomendado)
```
TAXA_RECEBIMENTO=0.025   (2.5%)
TAXA_SAQUE=0.01          (1%)
```

### Opção 3: Maiores taxas (Lucro alto)
```
TAXA_RECEBIMENTO=0.05    (5%)
TAXA_SAQUE=0.03          (3%)
```

### Opção 4: Apenas taxa de saque
```
TAXA_RECEBIMENTO=0       (Cliente não paga)
TAXA_SAQUE=0.05          (Vendedor paga 5%)
```

---

## 📝 Comandos de Configuração

### Ver/Alterar Taxas
```bash
!config_taxas 0.025 0.01
```

### Dar Cargo de Vendedor
```bash
!dar_role_vendedor @usuario
```

### Ver Todos os Usuários
```bash
!listar_usuarios
```

### Adicionar/Remover Saldo (Admin)
```bash
!adicionar_saldo USER_ID 100
!remover_saldo USER_ID 50
```

---

## 🔐 Segurança

- ✅ Apenas usuários com o cargo podem cobrar/sacar
- ✅ Apenas dono pode alterar taxas
- ✅ Todas as transações são registradas
- ✅ Banco de dados protegido (SQLite)

---

## 💡 Dicas

1. **Comece com taxas baixas** (0.5% - 2%) para atrair vendedores
2. **Aumente gradualmente** conforme crescer
3. **Comunique as taxas** claramente aos vendedores
4. **Faça backup** do `bot.db` regularmente
5. **Teste em sandbox** antes de produção

---

## 🐛 Troubleshooting

| Problema | Solução |
|----------|---------|
| Comando `/cobrar` não funciona | Verifique se o usuário tem o cargo ou é dono |
| Taxas não aparecem | Reinicie o bot depois de alterar `.env` |
| Saldo não está correto | Use `!listar_usuarios` para verificar |
| Cargo não aparece | Verifique o `VENDEDOR_ROLE_ID` no `.env` |
