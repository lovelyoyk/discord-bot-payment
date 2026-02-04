#!/usr/bin/env python3
"""
Script para sincronizar comandos com o Discord API
"""

import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()

intents = discord.Intents.all()
intents.message_content = True
intents.members = True
intents.presences = True

bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")
    print(f"📍 Sincronizando comandos com Discord...")
    try:
        # Carregar cogs
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py") and not filename.startswith("__"):
                try:
                    await bot.load_extension(f"cogs.{filename[:-3]}")
                    print(f"✅ Cog carregado: {filename}")
                except Exception as e:
                    print(f"❌ Erro ao carregar {filename}: {e}")
        
        # Sincronizar
        synced = await bot.tree.sync()
        print(f"✅ {len(synced)} slash commands sincronizados:")
        for cmd in synced:
            print(f"   - /{cmd.name}")
        
        # Desconectar após sincronização
        await bot.close()
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        await bot.close()

# Executar bot
token = os.getenv("DISCORD_TOKEN")
if token:
    asyncio.run(bot.start(token))
else:
    print("❌ DISCORD_TOKEN não encontrado no .env")
