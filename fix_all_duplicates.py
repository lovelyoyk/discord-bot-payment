#!/usr/bin/env python3
"""
Script para deletar TODOS os comandos globais e manter apenas os do GUILD
"""
import requests
import os
from collections import Counter

# Carregar .env sem dependências
def load_env():
    env = {}
    env_file = "/opt/discord-bot/.env"
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"\'')
                    env[key] = value
    return env

env = load_env()
TOKEN = env.get("DISCORD_TOKEN")
GUILD_ID = env.get("GUILD_ID")
BOT_ID = env.get("BOT_ID", "1468341807350808576")

if not TOKEN or not GUILD_ID:
    print("❌ Tokens não definidos!")
    exit(1)

headers = {
    "Authorization": f"Bot {TOKEN}",
    "Content-Type": "application/json"
}

print("=" * 60)
print("🔍 VERIFICANDO COMANDOS GLOBAIS E DO GUILD")
print("=" * 60)

# 1. Listar comandos GLOBAIS
print("\n1️⃣ Comandos GLOBAIS:")
response = requests.get(
    f"https://discord.com/api/v10/applications/{BOT_ID}/commands",
    headers=headers
)
global_commands = response.json()
print(f"   Total: {len(global_commands)} comandos")

if global_commands:
    print("   Nomes: ", ", ".join([cmd['name'] for cmd in global_commands]))

# 2. Listar comandos do GUILD
print(f"\n2️⃣ Comandos do GUILD ({GUILD_ID}):")
response = requests.get(
    f"https://discord.com/api/v10/applications/{BOT_ID}/guilds/{GUILD_ID}/commands",
    headers=headers
)
guild_commands = response.json()
print(f"   Total: {len(guild_commands)} comandos")
guild_names = [cmd['name'] for cmd in guild_commands]
print(f"   Nomes: {', '.join(sorted(guild_names))}")

# 3. Checar duplicatas no GUILD
print(f"\n3️⃣ Verificando duplicatas no GUILD:")
counter = Counter(guild_names)
duplicates = {name: count for name, count in counter.items() if count > 1}

if duplicates:
    print(f"   ⚠️  DUPLICATAS ENCONTRADAS:")
    for name, count in duplicates.items():
        print(f"       - /{name}: {count} vezes")
        cmd_ids = [cmd['id'] for cmd in guild_commands if cmd['name'] == name]
        for i, cmd_id in enumerate(cmd_ids, 1):
            print(f"         ID: {cmd_id} (cópia #{i})")
else:
    print(f"   ✅ Nenhuma duplicata no GUILD")

# 4. DELETAR TODOS os comandos globais (eles causam duplicação)
print(f"\n4️⃣ Deletando comandos GLOBAIS:")
if global_commands:
    for cmd in global_commands:
        response = requests.delete(
            f"https://discord.com/api/v10/applications/{BOT_ID}/commands/{cmd['id']}",
            headers=headers
        )
        if response.status_code == 204:
            print(f"   ✅ Deletado: /{cmd['name']} (ID: {cmd['id']})")
        else:
            print(f"   ❌ Erro: /{cmd['name']} - {response.status_code}")
    print("\n   ⚠️  IMPORTANTE: Agora os comandos só existem no GUILD")
    print("      Eles aparecerão instantaneamente em 'LS Aluguel - Financeiro'")
    print("      Mas podem levar até 1 hora para aparecer em outros servidores")
else:
    print("   ✅ Nenhum comando global para deletar")

# 5. DELETAR DUPLICATAS NO GUILD se existirem
if duplicates:
    print(f"\n5️⃣ Deletando duplicatas no GUILD:")
    for name, count in duplicates.items():
        cmd_ids = [cmd['id'] for cmd in guild_commands if cmd['name'] == name]
        # Manter o primeiro, deletar os demais
        for cmd_id in cmd_ids[1:]:
            response = requests.delete(
                f"https://discord.com/api/v10/applications/{BOT_ID}/guilds/{GUILD_ID}/commands/{cmd_id}",
                headers=headers
            )
            if response.status_code == 204:
                print(f"   ✅ Deletado: /{name} (duplicata)")
            else:
                print(f"   ❌ Erro ao deletar /{name}")

print("\n" + "=" * 60)
print("✅ PROCESSO CONCLUÍDO!")
print("=" * 60)

# Verificação final
print("\n📊 VERIFICAÇÃO FINAL:")
response = requests.get(
    f"https://discord.com/api/v10/applications/{BOT_ID}/guilds/{GUILD_ID}/commands",
    headers=headers
)
final_commands = response.json()
final_names = [cmd['name'] for cmd in final_commands]
print(f"\n   GUILD: {len(final_commands)} comandos")
if len(final_names) != len(set(final_names)):
    print(f"   ❌ AINDA TEM DUPLICATAS!")
else:
    print(f"   ✅ Sem duplicatas!")
    print(f"   Comandos: {', '.join(sorted(final_names))}")

response = requests.get(
    f"https://discord.com/api/v10/applications/{BOT_ID}/commands",
    headers=headers
)
global_final = response.json()
print(f"\n   GLOBAL: {len(global_final)} comandos")
if global_final:
    print(f"   ⚠️  Ainda existem comandos globais: {', '.join([cmd['name'] for cmd in global_final])}")
else:
    print(f"   ✅ Nenhum comando global")
