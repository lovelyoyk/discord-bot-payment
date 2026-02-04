#!/usr/bin/env python3
"""
Script para deletar TODOS os comandos globais com retry e delay
"""
import requests
import os
import time
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

print("🔄 Deletando TODOS os comandos globais com retry...")

# Loop até deletar todos
max_attempts = 3
for attempt in range(max_attempts):
    response = requests.get(
        f"https://discord.com/api/v10/applications/{BOT_ID}/commands",
        headers=headers
    )
    global_commands = response.json()
    
    if not global_commands:
        print(f"✅ Sucesso! Nenhum comando global restante.")
        break
    
    print(f"\n🔄 Tentativa {attempt + 1}: Deletando {len(global_commands)} comandos globais...")
    
    for cmd in global_commands:
        response = requests.delete(
            f"https://discord.com/api/v10/applications/{BOT_ID}/commands/{cmd['id']}",
            headers=headers
        )
        
        if response.status_code == 204:
            print(f"   ✅ /{cmd['name']}")
        elif response.status_code == 429:
            # Rate limited, aguardar
            retry_after = float(response.headers.get('Retry-After', 1))
            print(f"   ⏱️  Rate limited (aguardando {retry_after}s)...")
            time.sleep(retry_after)
            # Retry
            response = requests.delete(
                f"https://discord.com/api/v10/applications/{BOT_ID}/commands/{cmd['id']}",
                headers=headers
            )
            if response.status_code == 204:
                print(f"   ✅ /{cmd['name']} (retry)")
            else:
                print(f"   ❌ /{cmd['name']} - erro {response.status_code}")
        else:
            print(f"   ❌ /{cmd['name']} - erro {response.status_code}")
        
        time.sleep(0.5)  # Pequeno delay entre requisições
    
    if attempt < max_attempts - 1:
        time.sleep(2)

# Verificação final
print("\n" + "="*60)
response = requests.get(
    f"https://discord.com/api/v10/applications/{BOT_ID}/commands",
    headers=headers
)
final_global = response.json()

print(f"📊 Resultado final:")
print(f"   GLOBAL: {len(final_global)} comandos")

if final_global:
    print(f"   ⚠️  Ainda existem: {', '.join([cmd['name'] for cmd in final_global])}")
else:
    print(f"   ✅ TODOS OS COMANDOS GLOBAIS DELETADOS!")
