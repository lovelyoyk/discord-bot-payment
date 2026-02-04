"""
Componentes de UI para o Sistema de Carteira e Pagamentos
"""

import discord
from discord.ext import commands
from datetime import datetime

class CarteiraView(discord.ui.View):
    """View para o comando /meusdados com botões de ações."""
    
    def __init__(self, user_id: int, timeout: int = 180):
        super().__init__(timeout=timeout)
        self.user_id = user_id
        self.action = None
    
    @discord.ui.button(label="💳 Sacar", style=discord.ButtonStyle.success, emoji="💸")
    async def botao_sacar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Você não pode usar este botão!", ephemeral=True)
            return
        
        self.action = "sacar"
        self.stop()
        await interaction.response.defer()
    
    @discord.ui.button(label="🗑️ Apagar Dados", style=discord.ButtonStyle.danger, emoji="⚠️")
    async def botao_apagar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Você não pode usar este botão!", ephemeral=True)
            return
        
        self.action = "apagar"
        self.stop()
        await interaction.response.defer()
    
    @discord.ui.button(label="❌ Cancelar", style=discord.ButtonStyle.secondary, emoji="✖️")
    async def botao_cancelar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Você não pode usar este botão!", ephemeral=True)
            return
        
        self.action = None
        self.stop()
        await interaction.response.defer()

class ConfirmarAcaoView(discord.ui.View):
    """View para confirmar ações críticas."""
    
    def __init__(self, timeout: int = 60):
        super().__init__(timeout=timeout)
        self.confirmed = None
    
    @discord.ui.button(label="✅ Confirmar", style=discord.ButtonStyle.danger, emoji="☑️")
    async def botao_confirmar(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.confirmed = True
        self.stop()
        await interaction.response.defer()
    
    @discord.ui.button(label="❌ Cancelar", style=discord.ButtonStyle.secondary, emoji="✖️")
    async def botao_cancelar(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.confirmed = False
        self.stop()
        await interaction.response.defer()

class SacarView(discord.ui.View):
    """View para o comando de saque."""
    
    def __init__(self, user_id: int, timeout: int = 300):
        super().__init__(timeout=timeout)
        self.user_id = user_id
        self.action = None
    
    @discord.ui.button(label="✅ Confirmar Saque", style=discord.ButtonStyle.success, emoji="💸")
    async def botao_confirmar_saque(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Você não pode usar este botão!", ephemeral=True)
            return
        
        self.action = "confirmar"
        self.stop()
        await interaction.response.defer()
    
    @discord.ui.button(label="❌ Cancelar", style=discord.ButtonStyle.danger, emoji="✖️")
    async def botao_cancelar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Você não pode usar este botão!", ephemeral=True)
            return
        
        self.action = "cancelar"
        self.stop()
        await interaction.response.defer()

def criar_embed_carteira(
    username: str,
    saldo: float,
    transacoes: list,
    emoji_sucesso: str = "🟢",
    emoji_falha: str = "🟡"
) -> discord.Embed:
    """Cria um embed formatado para a carteira do usuário."""
    
    embed = discord.Embed(
        title="💼 Carteira & Extrato",
        description=f"Usuário: **{username}**",
        color=discord.Color.blue()
    )
    
    # Saldo disponível
    saldo_formatado = f"R$ {saldo:,.2f}".replace(",", ".")
    embed.add_field(
        name="💰 Saldo Disponível",
        value=f"**{saldo_formatado}**",
        inline=False
    )
    
    # Transações
    if transacoes:
        transacoes_text = "```"
        for trans in transacoes[:10]:  # Últimas 10
            tipo, valor, bruto, desc, sender, ref, status, data = trans
            
            status_emoji = emoji_sucesso if status == "completed" else emoji_falha
            
            # Formatar data
            data_obj = datetime.fromisoformat(data)
            data_fmt = data_obj.strftime("%d/%m %H:%M")
            
            # Formatar valor
            valor_fmt = f"R$ {valor:.2f}".replace(",", ".")
            bruto_fmt = f"R$ {bruto:.2f}".replace(",", ".") if bruto else "N/A"
            
            transacoes_text += f"\n{data_fmt} {status_emoji} +{valor_fmt} (Bruto: {bruto_fmt})"
            
            if sender:
                transacoes_text += f"\n└ De: @{sender}"
            
            if tipo == "refund" or status == "completed":
                transacoes_text += " ✅"
            elif status == "pending":
                transacoes_text += " ⏳"
        
        transacoes_text += "\n```"
        
        embed.add_field(
            name="📋 Últimas 10 Transações",
            value=transacoes_text,
            inline=False
        )
    else:
        embed.add_field(
            name="📋 Últimas 10 Transações",
            value="Nenhuma transação registrada",
            inline=False
        )
    
    embed.set_footer(text="Valores em verde são confirmados | Amarelo = pendente")
    return embed

def criar_embed_notificacao_pagamento(
    cliente: str,
    vendedor: str,
    valor: float,
    valor_bruto: float,
    ref: str,
    emoji_sucesso: str = "🟢"
) -> discord.Embed:
    """Cria um embed formatado para notificação de pagamento no canal."""
    
    valor_fmt = f"R$ {valor:.2f}".replace(",", ".")
    valor_bruto_fmt = f"R$ {valor_bruto:.2f}".replace(",", ".")
    
    embed = discord.Embed(
        title=f"{emoji_sucesso} Venda Aprovada!",
        description=f"O pagamento de **{valor_fmt}** foi confirmado.",
        color=discord.Color.green()
    )
    
    embed.add_field(
        name="👥 Cliente",
        value=f"@{cliente}",
        inline=True
    )
    
    embed.add_field(
        name="👤 Vendedor",
        value=f"@{vendedor}",
        inline=True
    )
    
    embed.add_field(
        name="💰 Valor Líquido",
        value=f"**{valor_fmt}**",
        inline=True
    )
    
    embed.add_field(
        name="📊 Valor Bruto",
        value=valor_bruto_fmt,
        inline=True
    )
    
    embed.add_field(
        name="📌 Referência",
        value=f"`{ref}`",
        inline=False
    )
    
    embed.set_footer(text="Saldo atualizado automaticamente")
    return embed
