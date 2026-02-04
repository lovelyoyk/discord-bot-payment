# ✨ Novas Features - Sistema de Cobrança v2

## 🎯 O que Mudou

### Antes ❌
```bash
!cobrar 50 "Descrição"
```
- Valor fixo para o próprio vendedor
- Sem seleção de cliente
- Sem opção de taxa

### Agora ✅
```bash
!cobrar @cliente 50 sim
```
- Menciona o cliente que receberá
- Escolhe se repassa taxa ou absorve
- Botão "Pagar Agora" interativo
- QR Code automático

---

## 🆕 Recursos Adicionados

### 1. **Botão "Pagar Agora"** 💳
- Clicável diretamente no Discord
- Abre o link de pagamento em mensagem privada
- Melhor experiência do usuário

### 2. **Seleção de Cliente** 👥
- Escolha qual usuário receberá o pagamento
- Suporte completo com menção (`@usuario`)
- Saldo separado por pessoa

### 3. **Opção de Repasse de Taxa** 🔄
- `sim` → Taxa repassada ao cliente
- `nao` → Você absorve a taxa
- Taxas calculadas automaticamente

### 4. **Embed Detalhado** 📋
Mostra claramente:
- Vendedor e Cliente
- Valor do serviço
- Valor da taxa
- Total a pagar
- ID da cobrança

---

## 📊 Exemplo Visual

```
💳 Cobrança de Serviço
Fatura gerada para @João

👤 Vendedor: @Você
👥 Cliente: @João

📋 Serviço
R$ 1,00

📊 Taxas
+ R$ 0,65 (Taxa 2.5% - Repassada ao cliente)

💰 Total a Pagar
R$ 1,65

📌 ID da Cobrança
`abc123def456`

[💳 Pagar Agora] ← Botão clicável
```

---

## 🔧 Arquivos Novos

- `ui_components.py` - Componentes reutilizáveis (Views, Buttons)
- `GUIA_COBRAR.md` - Documentação completa do novo sistema

---

## 🎮 Como Usar

### Básico
```bash
!cobrar @João 100
```
(Usa padrão: taxa repassada = sim)

### Com Taxa Repassada
```bash
!cobrar @João 100 sim
```
Cliente paga a taxa extras

### Com Taxa Absorvida
```bash
!cobrar @João 100 nao
```
Você paga a taxa

---

## 💡 Casos de Uso

### Use **SIM** quando:
- Você quer maximizar lucro
- O cliente concorda com taxa
- É uma cobrança de alto valor

### Use **NÃO** quando:
- Quer fidelizar cliente
- Oferecendo desconto
- Valor fixo negociado

---

## ⚙️ Compatibilidade

✅ Discord.py 2.0+  
✅ Python 3.10+  
✅ MisticPay  
✅ Todos os navegadores

---

## 🚀 Próximos Passos

- [ ] Adicionar relatórios de cobrança
- [ ] Notificações automáticas de pagamento
- [ ] Histórico de cobranças por cliente
- [ ] Cupons de desconto
- [ ] Integração com Google Sheets

---

Aproveite o novo sistema! 🎉
