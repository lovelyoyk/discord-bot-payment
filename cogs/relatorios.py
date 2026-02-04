import discord
from discord.ext import commands
from discord import app_commands
import os
import sqlite3
from datetime import datetime, timedelta
from database import get_balance, get_total_balance, get_transaction_history
from embed_utils import padronizar_embed

class RelatoriosCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = os.getenv("DATABASE_PATH", "./data/bot.db")
    
    @app_commands.command(name="dashboard", description="Mostra um dashboard com resumo de saldos e transações")
    async def dashboard(self, interaction: discord.Interaction):
        """Mostra um dashboard com resumo de saldos e transações."""
        user_id = interaction.user.id
        
        # Obter saldo
        saldo = get_balance(user_id)
        
        # Obter histórico
        historico = get_transaction_history(user_id, limit=5)
        
        # Obter total de ganhos (sum de transações de entrada)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Verificar se tabela transactions existe, senão usar valores padrão
        try:
            cursor.execute("""
                SELECT 
                    SUM(CASE WHEN tipo IN ('add', 'payment', 'deposit') THEN valor ELSE 0 END) as ganhos,
                    COUNT(CASE WHEN tipo = 'withdraw' THEN 1 END) as num_saques,
                    SUM(CASE WHEN tipo = 'withdraw' THEN valor ELSE 0 END) as total_sacado
                FROM transactions
                WHERE user_id = ?
            """, (user_id,))
        except sqlite3.OperationalError:
            # Tabela não existe, usar valores padrão
            cursor.execute("SELECT 0, 0, 0")
        
        resultado = cursor.fetchone()
        ganhos = resultado[0] or 0
        num_saques = resultado[1] or 0
        total_sacado = resultado[2] or 0
        
        conn.close()
        
        from embed_utils import criar_separador, formatar_valor, criar_barra_progresso
        
        # Criar embed
        embed = discord.Embed(
            title="📊 Seu Dashboard Financeiro",
            description=f"{criar_separador('VISÃO GERAL')}",
            color=discord.Color.blue()
        )
        
        # Calcular porcentagem de saldo em relação ao total ganho
        if ganhos > 0:
            porcentagem_saldo = int((saldo / ganhos) * 100)
        else:
            porcentagem_saldo = 0
        
        embed.add_field(
            name="💰 Saldo Disponível",
            value=formatar_valor(saldo),
            inline=True
        )
        
        embed.add_field(
            name="📈 Total Recebido",
            value=formatar_valor(ganhos),
            inline=True
        )
        
        embed.add_field(
            name="\u200b",
            value="\u200b",
            inline=False
        )
        
        embed.add_field(
            name="💸 Total Sacado",
            value=formatar_valor(total_sacado),
            inline=True
        )
        
        embed.add_field(
            name="🏦 Número de Saques",
            value=f"**{num_saques}** saque(s)",
            inline=True
        )
        
        # Gráfico de distribuição de saldo
        if ganhos > 0:
            embed.add_field(
                name=f"\n{criar_separador('DISTRIBUIÇÃO')}",
                value=f"💰 Saldo Atual: {criar_barra_progresso(porcentagem_saldo)}\n💸 Já Sacado: {criar_barra_progresso(100 - porcentagem_saldo)}",
                inline=False
            )
        
        # Últimas transações
        if historico:
            transacoes_text = ""
            for idx, (tipo, amount, description, created_at) in enumerate(historico[:3], 1):
                emoji = "➕" if tipo in ["add", "payment"] else "➖"
                valor_fmt = f"+R$ {amount:.2f}" if tipo in ["add", "payment"] else f"-R$ {amount:.2f}"
                transacoes_text += f"{emoji} **{idx}.** {description}\n   `{valor_fmt}` • {created_at[:10]}\n"
            
            embed.add_field(
                name=f"\n{criar_separador('ÚLTIMAS TRANSAÇÕES')}",
                value=transacoes_text,
                inline=False
            )
        else:
            embed.add_field(
                name=f"\n{criar_separador('ÚLTIMAS TRANSAÇÕES')}",
                value="*Nenhuma transação registrada ainda*",
                inline=False
            )
        
        padronizar_embed(embed, interaction, user=interaction.user, icone_tipo="dashboard")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(RelatoriosCog(bot))
