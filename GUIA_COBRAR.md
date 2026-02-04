# 🆕 Guia de Uso - Novo Sistema de Cobrança

## 📋 Comando `/cobrar` Atualizado

### Sintaxe
```bash
!cobrar @cliente valor repassar_taxa
```

### Parâmetros

| Parâmetro | Tipo | Descrição | Exemplo |
|-----------|------|-----------|---------|
| `@cliente` | Menção | Usuário que receberá o pagamento | `@João` |
| `valor` | Número | Valor em reais | `50` ou `150.50` |
| `repassar_taxa` | Sim/Não | Taxa repassada ao cliente ou absorvida | `sim` ou `nao` |

### Opções de `repassar_taxa`

- ✅ **Aceita:** `sim`, `s`, `yes`, `y`, `true`, `1`
- ❌ **Aceita:** `nao`, `n`, `no`, `false`, `0`

---

## 📱 Exemplos de Uso

### Exemplo 1: Cobrar com taxa repassada
```bash
!cobrar @João 100 sim
```

**Resultado:**
```
💳 Cobrança de Serviço
Fatura gerada para @João

👤 Vendedor: @Você
👥 Cliente: @João

📋 Serviço: R$ 100,00
📊 Taxas: + R$ 2,50 (Taxa 2.5% - Repassada ao cliente)
💰 Total a Pagar: R$ 102,50

[💳 Pagar Agora] ← Botão clickável
```

**O cliente paga:** R$ 102,50  
**João recebe no saldo:** R$ 102,50

---

### Exemplo 2: Cobrar com taxa absorvida
```bash
!cobrar @Maria 50 nao
```

**Resultado:**
```
💳 Cobrança de Serviço
Fatura gerada para @Maria

👤 Vendedor: @Você
👥 Cliente: @Maria

📋 Serviço: R$ 50,00
📊 Taxas: - R$ 1,25 (Taxa 2.5% - Absorvida pelo vendedor)
💰 Total a Pagar: R$ 50,00

[💳 Pagar Agora] ← Botão clickável
```

**O cliente paga:** R$ 50,00  
**Maria recebe no saldo:** R$ 50,00  
**Você paga a taxa:** R$ 1,25 (do seu saldo)

---

## 🔘 Botão "Pagar Agora"

Ao clicar no botão **💳 Pagar Agora**, o cliente recebe uma mensagem privada com o link de pagamento.

```
💳 Link de Pagamento
👉 Clique aqui para pagar 👈

Você será redirecionado para o pagamento
```

---

## 🧮 Cálculos de Taxa

### Cenário 1: Taxa Repassada (Padrão)
```
Valor original: R$ 100,00
Taxa: 2.5%
Cálculo: 100 × 1,025 = 102,50
Cliente paga: R$ 102,50
Saldo creditado: R$ 102,50
```

### Cenário 2: Taxa Absorvida
```
Valor original: R$ 100,00
Taxa: 2.5%
Cálculo: 100 - (100 × 0,025) = 97,50
Cliente paga: R$ 100,00
Saldo creditado: R$ 97,50
Você absorve: R$ 2,50
```

---

## 💰 Fluxo Completo

### Com Taxa Repassada (sim)
```
1. Você: !cobrar @Cliente 50 sim
   ↓
2. Bot calcula: 50 + (50 × 0.025) = R$ 51,25
   ↓
3. Cliente clica em "Pagar Agora"
   ↓
4. Cliente paga R$ 51,25
   ↓
5. MisticPay confirma
   ↓
6. Saldo de Cliente += R$ 51,25 ✅
```

### Com Taxa Absorvida (nao)
```
1. Você: !cobrar @Cliente 50 nao
   ↓
2. Bot calcula: 50 - (50 × 0.025) = R$ 48,75
   ↓
3. Cliente clica em "Pagar Agora"
   ↓
4. Cliente paga R$ 50,00
   ↓
5. MisticPay confirma
   ↓
6. Saldo de Cliente += R$ 50,00 ✅
   Seu saldo -= R$ 1,25 (taxa absorvida)
```

---

## ⚠️ Casos de Erro

### Erro 1: Usuário não é vendedor
```bash
!cobrar @João 50 sim
❌ Apenas vendedores ou o dono podem usar este comando.
```

### Erro 2: Valor inválido
```bash
!cobrar @João 0 sim
❌ O valor deve ser maior que R$ 0.
```

### Erro 3: Usuário não mencionado
```bash
!cobrar 50 sim
❌ User "50" not found
```

---

## 🎯 Quando Usar Cada Opção

### Use `sim` (Taxa Repassada) quando:
- ✅ Você quer absorver a taxa
- ✅ O cliente concorda em pagar a taxa
- ✅ Você quer saldo maior no final

### Use `nao` (Taxa Absorvida) quando:
- ❌ Você quer que o cliente pague um valor fixo
- ❌ Você absorve o custo da taxa
- ❌ É melhor para conversão de clientes

---

## 📊 Comparação de Estratégias

| Estratégia | Cliente Paga | Você Recebe | Taxa Absorvida |
|-----------|--------------|------------|-----------------|
| Taxa Repassada (sim) | R$ 102,50 | R$ 102,50 | Não |
| Taxa Absorvida (nao) | R$ 100,00 | R$ 100,00 | R$ 2,50 |

Para uma cobrança de R$ 100 com taxa de 2.5%.

---

## 💡 Dicas

1. **Teste ambas as opções** com clientes para ver qual converte melhor
2. **Comunique claramente** se a taxa será repassada ou não
3. **Configure taxas baixas** (0.5% - 2%) para melhor conversão
4. **Use "sim"** por padrão - clientes costumam aceitar

---

## 🎮 Integração com Bots

Se você usar o bot em grupo, todos com o cargo "Vendedor" podem cobrar:

```bash
# Você: vendedor
!cobrar @Cliente 100 sim ✅

# Outro vendedor:
!cobrar @Cliente 50 nao ✅

# Usuário comum:
!cobrar @Cliente 25 sim ❌ (Acesso negado)
```
