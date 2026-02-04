#!/usr/bin/env python3
"""
Script para limpar todos os comandos duplicados do Discord
"""
import discord
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()

async def clear_all_commands():
    intents = discord.Intents.default()
    intents.message_content = True
    
    async with discord.Client(intents=intents) as client:
        @client.event
        async def on_ready():
            try:
                # Limpar comandos globais
                print("🗑️ Limpando comandos globais...")
                await client.tree.sync()
                print("✅ Comandos globais limpos")
                
                # Limpar comandos da guild se GUILD_ID estiver set
                guild_id = os.getenv("GUILD_ID")
                if guild_id:
                    guild = discord.Object(id=int(guild_id))
                    print(f"🗑️ Limpando comandos da guild {guild_id}...")
                    await client.tree.sync(guild=guild)
                    print(f"✅ Comandos da guild {guild_id} limpos")
                
                await client.close()
            except Exception as e:
                print(f"❌ Erro: {e}")
                import traceback
                traceback.print_exc()
                await client.close()
        
        token = os.getenv("DISCORD_TOKEN")
        await client.start(token)

if __name__ == "__main__":
    asyncio.run(clear_all_commands())
