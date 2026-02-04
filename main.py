import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from database import init_db
from pathlib import Path
import asyncio

# Carregar variáveis de ambiente
load_dotenv()

# Inicializar sistemas auxiliares
from utils.logger import setup_logger
from utils.backup import BackupManager
from utils.uptime_monitor import uptime_monitor

# Configurar logger
logger = setup_logger("bot")
logger.info("🚀 Iniciando bot...")

# Inicializar banco de dados
init_db()
logger.info("✅ Banco de dados inicializado")

# Configurar backup automático
db_path = os.getenv("DATABASE_PATH", "./data/bot.db")
backup_manager = BackupManager(db_path)
backup_manager.start_scheduled_backups(hour=3, minute=0)
logger.info("✅ Sistema de backup configurado")

# Iniciar monitor de uptime
uptime_monitor.start_monitoring()

# Configurar bot
intents = discord.Intents.all()
intents.message_content = True
intents.members = True
intents.presences = True
bot = commands.Bot(command_prefix="/", intents=intents)

# Variável global para webhook acessar bot
import webhook_server
webhook_server.bot_instance = bot
webhook_server.logger = logger

# Iniciar servidor webhook em thread separada
import threading
webhook_thread = threading.Thread(target=webhook_server.run_webhook, daemon=True)
webhook_thread.start()
logger.info("✅ Servidor webhook iniciado na porta 5000")
print("🌐 Servidor webhook rodando em http://0.0.0.0:5000")

@bot.event
async def on_ready():
    logger.info(f"✅ Bot conectado como {bot.user}")
    print(f"✅ Bot conectado como {bot.user}")
    
    # Atualizar heartbeat
    uptime_monitor.heartbeat()
    
    try:
        # Carregar cogs
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py") and not filename.startswith("__"):
                try:
                    await bot.load_extension(f"cogs.{filename[:-3]}")
                    logger.info(f"✅ Cog carregado: {filename}")
                    print(f"✅ Cog carregado: {filename}")
                except Exception as cog_error:
                    logger.error(f"❌ Erro ao carregar {filename}: {cog_error}")
                    print(f"❌ Erro ao carregar {filename}: {cog_error}")
        
        # Sincronizar slash commands com timeout
        try:
            print(f"📍 Iniciando sincronização de comandos...")
            logger.info("Sincronizando comandos...")
            print(f"📍 Total de comandos registrados: {len(bot.tree._get_all_commands())}")
            
            # Sincronizar com timeout de 30 segundos
            try:
                synced = await asyncio.wait_for(bot.tree.sync(), timeout=30.0)
                logger.info(f"✅ {len(synced)} comandos sincronizados")
                print(f"✅ {len(synced)} slash commands sincronizados com sucesso!")
                for cmd in synced:
                    print(f"   - /{cmd.name}")
            except asyncio.TimeoutError:
                logger.warning("⚠️ Timeout na sincronização de comandos")
                print(f"⚠️  Sincronização demorou muito, continuando sem resultado visível...")
        except Exception as e:
            logger.error(f"Erro ao sincronizar comandos: {e}")
            print(f"❌ Erro ao sincronizar commands: {e}")
            import traceback
            traceback.print_exc()
    except Exception as e:
        logger.error(f"Erro ao carregar cogs: {e}")
        print(f"❌ Erro ao carregar cogs: {e}")
        import traceback
        traceback.print_exc()

@bot.event
async def on_command_error(ctx, error):
    """Handler global de erros"""
    logger.error(f"Erro no comando {ctx.command}: {error}")
    uptime_monitor.log_error(error)

@bot.command(name="ajuda")
async def help_cmd(ctx):
    """Mostra todos os comandos disponíveis."""
    embed = discord.Embed(
        title="📖 Ajuda - Comandos Disponíveis",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="� Configuração",
        value="```\n" +
              "!pix <chave> - Definir sua chave PIX\n" +
              "```",
        inline=False
    )
    
    embed.add_field(
        name="💰 Saldos (Público)",
        value="```\n" +
              "!saldo - Ver seu saldo pessoal\n" +
              "!saldo_geral - Ver saldo total\n" +
              "!historico - Ver suas transações\n" +
              "```",
        inline=False
    )
    
    embed.add_field(
        name="💳 Pagamentos (Vendedores)",
        value="```\n" +
              "!cobrar @cliente <valor> [sim/nao] - Gerar cobrança com QR + Botão\n" +
              "!sacar [valor] - Sacar saldo para PIX\n" +
              "```",
        inline=False
    )
    
    embed.add_field(
        name="🔐 Admin (Apenas Dono)",
        value="```\n" +
              "!adicionar_saldo <user_id> <valor>\n" +
              "!remover_saldo <user_id> <valor>\n" +
              "!listar_usuarios\n" +
              "!dar_role_vendedor [@user]\n" +
              "!config_taxas <taxa_recebimento> <taxa_saque>\n" +
              "```",
        inline=False
    )
    
    await ctx.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Falta argumento: {error.param.name}")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Argumento inválido. Verifique o tipo de dado.")
    else:
        await ctx.send(f"❌ Erro: {error}")

if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("❌ DISCORD_TOKEN não configurado no .env")
        exit(1)
    bot.run(token)
