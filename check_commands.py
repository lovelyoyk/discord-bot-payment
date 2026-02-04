#!/usr/bin/env python3
"""
Script para verificar todos os comandos registrados no servidor Discord
"""
import discord
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID", 0))

async def main():
    intents = discord.Intents.default()
    client = discord.Client(intents=intents)
    
    @client.event
    async def on_ready():
        print(f"✅ Bot conectado como {client.user}")
        
        if GUILD_ID:
            guild = client.get_guild(GUILD_ID)
            if guild:
                print(f"\n📍 Verificando servidor: {guild.name} ({GUILD_ID})")
                
                # Pega todos os comandos
                commands = await guild.fetch_commands()
                
                print(f"\n📊 Total de comandos: {len(commands)}\n")
                
                # Conta ocorrências
                command_names = {}
                for cmd in commands:
                    if cmd.name not in command_names:
                        command_names[cmd.name] = 0
                    command_names[cmd.name] += 1
                
                # Mostra todas as entradas
                for i, cmd in enumerate(commands, 1):
                    dup_marker = " 🔴 DUPLICADO" if command_names[cmd.name] > 1 else ""
                    print(f"{i:2}. /{cmd.name:<20} (ID: {cmd.id}){dup_marker}")
                
                # Resume
                print("\n" + "="*50)
                duplicated = {k: v for k, v in command_names.items() if v > 1}
                if duplicated:
                    print(f"⚠️  Comandos duplicados encontrados:")
                    for name, count in duplicated.items():
                        print(f"   - /{name}: {count} vezes")
                else:
                    print("✅ Nenhum comando duplicado encontrado!")
        
        await client.close()
    
    await client.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
