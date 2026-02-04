# 🎨 Guia de Emojis Customizáveis

## Emojis Disponíveis para Configuração

Você pode customizar os seguintes emojis adicionando as variáveis no arquivo `.env`:

### 1. **EMOJI_SUCESSO** ✅
- **Uso**: Indica sucesso em notificações e operações bem-sucedidas
- **Padrão**: `✅`
- **Exemplo**: `EMOJI_SUCESSO=<a:check_yes:1429518291644997693>`

### 2. **EMOJI_CLIENTE** 👥
- **Uso**: Marca o cliente/pagador em notificações de pagamento
- **Padrão**: `👥`
- **Exemplo**: `EMOJI_CLIENTE=<:member:1461081150567129129>`

### 3. **EMOJI_VENDEDOR** 👤
- **Uso**: Marca o vendedor/recebedor em notificações
- **Padrão**: `👤`
- **Exemplo**: `EMOJI_VENDEDOR=<:SUPORTE:1461101196803244042>`

### 4. **EMOJI_VALOR** 💰
- **Uso**: Marca valores em transações e saldos
- **Padrão**: `💰`
- **Exemplo**: `EMOJI_VALOR=<:dinheiro1:1461111125268045874>`

### 5. **EMOJI_PAGAMENTO** 💳
- **Uso**: Marca status de pagamento e transações
- **Padrão**: `💳`
- **Exemplo**: `EMOJI_PAGAMENTO=<a:am_rd_spc:1461222228936323072>`

---

## Como Usar Emojis Customizados

### Opção 1: Emojis Unicode (Padrão)
```
EMOJI_SUCESSO=✅
EMOJI_CLIENTE=👥
EMOJI_VALOR=💰
```

### Opção 2: Emojis Customizados do Discord
```
EMOJI_SUCESSO=<a:check_yes:1429518291644997693>
EMOJI_CLIENTE=<:member:1461081150567129129>
EMOJI_VALOR=<:dinheiro1:1461111125268045874>
```

---

## Como Encontrar o ID de um Emoji Customizado

1. **No Discord**, envie uma mensagem com `\:emoji_name:`
2. **Copie o resultado** que aparecerá como: `<:emoji_name:123456789>`
3. **Cole no `.env`** do seu servidor

---

## Exemplos Reais (Seu Servidor)

```env
EMOJI_SUCESSO=<a:check_yes:1429518291644997693>
EMOJI_CLIENTE=<:member:1461081150567129129>
EMOJI_VENDEDOR=<:SUPORTE:1461101196803244042>
EMOJI_VALOR=<:dinheiro1:1461111125268045874>
EMOJI_PAGAMENTO=<a:am_rd_spc:1461222228936323072>
```

---

## Locais de Uso

### Emojis são exibidos em:

1. **EMOJI_SUCESSO**: 
   - ✅ Transações bem-sucedidas
   - ✅ Operações completadas

2. **EMOJI_CLIENTE**: 
   - Em notificações de pagamento
   - Mensagens de entrada de cliente

3. **EMOJI_VENDEDOR**: 
   - Em notificações de recebimento
   - Mensagens de vendedor/recebedor

4. **EMOJI_VALOR**: 
   - Valores em transações
   - Saldos e relatórios

5. **EMOJI_PAGAMENTO**: 
   - Status de pagamento
   - Notificações de transações

---

## Dica Importante! 💡

- Os emojis **customizados do Discord devem pertencer a um servidor** que o bot tenha acesso
- Se usar um emoji de outro servidor, o Discord mostrará um `❓` no lugar
- **Unicode emojis sempre funcionam** em qualquer lugar

Para adicionar novo emoji ao seu servidor:
1. Vá em Configurações > Emojis > Enviar Emoji
2. Faça upload da imagem
3. Copie o ID com `\:nome_emoji:`
4. Cole no `.env`
