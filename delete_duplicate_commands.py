#!/usr/bin/env python3
"""
Script para deletar comandos duplicados diretamente via API do Discord
Usa requests em vez de discord.py para mais controle
"""
import requests
import os
from dotenv import load_dotenv
from collections import Counter

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")
BOT_ID = os.getenv("BOT_ID", "1468341807350808576")  # ID do bot

if not TOKEN or not GUILD_ID:
    print("❌ BOT_TOKEN ou GUILD_ID não definido!")
    exit(1)

headers = {
    "Authorization": f"Bot {TOKEN}",
    "Content-Type": "application/json"
}

# 1. Listar todos os comandos do servidor
print("📍 Verificando comandos no servidor...")
response = requests.get(
    f"https://discord.com/api/v10/applications/{BOT_ID}/guilds/{GUILD_ID}/commands",
    headers=headers
)

if response.status_code != 200:
    print(f"❌ Erro ao listar comandos: {response.status_code} - {response.text}")
    exit(1)

commands = response.json()
print(f"✅ Total de comandos encontrados: {len(commands)}\n")

# 2. Detectar duplicatas
command_names = [cmd['name'] for cmd in commands]
command_counter = Counter(command_names)
duplicates = {name: count for name, count in command_counter.items() if count > 1}

if not duplicates:
    print("✅ Nenhum comando duplicado encontrado!")
    exit(0)

# 3. Mostrar duplicatas
print(f"⚠️  Comandos duplicados encontrados:\n")
for name, count in duplicates.items():
    print(f"   /{name}: {count} vezes")
    # Encontrar IDs dos duplicados
    cmd_ids = [cmd['id'] for cmd in commands if cmd['name'] == name]
    for i, cmd_id in enumerate(cmd_ids, 1):
        print(f"      - ID: {cmd_id} (cópia #{i})")

# 4. Deletar duplicatas (mantém o primeiro, deleta os demais)
print(f"\n🗑️  Deletando duplicatas...\n")
for name, count in duplicates.items():
    cmd_ids = [cmd['id'] for cmd in commands if cmd['name'] == name]
    # Manter o primeiro, deletar os demais
    for cmd_id in cmd_ids[1:]:
        response = requests.delete(
            f"https://discord.com/api/v10/applications/{BOT_ID}/guilds/{GUILD_ID}/commands/{cmd_id}",
            headers=headers
        )
        if response.status_code == 204:
            print(f"✅ Deletado: /{name} (ID: {cmd_id})")
        else:
            print(f"❌ Erro ao deletar /{name} (ID: {cmd_id}): {response.status_code}")

print(f"\n✅ Processo concluído!")

# 5. Listar novos comandos
response = requests.get(
    f"https://discord.com/api/v10/applications/{BOT_ID}/guilds/{GUILD_ID}/commands",
    headers=headers
)
new_commands = response.json()
print(f"\n📊 Novos comandos após limpeza: {len(new_commands)}")
