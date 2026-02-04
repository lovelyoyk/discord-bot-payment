# 👤 Configuração de Aprovadores

## O que são Aprovadores?

**Aprovadores** são usuários autorizados a aprovar ou rejeitar solicitações de **reembolso** enviadas pelo comando `/reembolsar`.

Quando alguém solicita um reembolso:
1. O sistema cria uma solicitação
2. Envia um **DM (mensagem privada)** para cada aprovador
3. O aprovador pode **Aprovar** ✅ ou **Rejeitar** ❌
4. Se aprovado, o saldo é reembolsado para o usuário

---

## Como Configurar Aprovadores

### 1. Encontre o ID de cada aprovador no Discord

**Método 1 - No Discord:**
- Mencione a pessoa com `@usuario`
- Se tiver "Modo desenvolvedor" ativado, clique com botão direito no usuário → "Copiar ID"

**Método 2 - Via bot:**
- Use `/meusdados` para ver seu próprio ID
- Peça para o usuário usar o comando também

### 2. Adicione no arquivo `.env`

```env
APROVADORES_REEMBOLSO=123456789,987654321,111111111
```

**Explicação:**
- Separe os IDs com **vírgula** (`,`)
- Sem espaços entre os números
- Coloque quantos aprovadores precisar

### 3. Exemplo Real

Se você quer que **3 pessoas** aprovem reembolsos:
```env
APROVADORES_REEMBOLSO=1461089506521169922,1461089506521169923,1461089506521169924
```

---

## Testando a Configuração

1. **Reinicie o bot** (após salvar o `.env`)
2. Alguém usa `/reembolsar @usuario valor motivo`
3. Os aprovadores receberão uma DM com:
   - Detalhes do reembolso
   - Botão para Aprovar ✅
   - Botão para Rejeitar ❌

---

## Sistema de Financeiros (Alternativo)

Você também pode usar o comando `/adicionar-financeiro` para gerenciar aprovadores de forma dinâmica (sem editar `.env`):

```
/adicionar-financeiro @usuario
```

Os usuários adicionados como "financeiro" podem:
- Aprovar reembolsos
- Aprovar saques

---

## Importante! ⚠️

- Se não configurar nenhum aprovador, a mensagem "❌ Nenhum aprovador configurado..." aparecerá
- Os aprovadores recebem a solicitação **em DM privada** (não no canal público)
- O bot precisa conseguir enviar DM para o aprovador (privado aberto)

