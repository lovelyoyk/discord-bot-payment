"""
Cog para gerenciar financeiros e aprovar saques/reembolsos
"""

import discord
from discord.ext import commands
from discord import app_commands
from database import (
    add_financeiro, remove_financeiro, is_financeiro, 
    get_all_financeiros, get_financeiro_info
)
import os

ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

class FinanceiroModal(discord.ui.Modal, title="Detalhes da Aprovação"):
    """Modal para registrar detalhes da aprovação/rejeição"""
    observacao = discord.ui.TextInput(
        label="Observações (opcional)",
        placeholder="Ex: Transferência concluída em 2min...",
        max_length=500,
        required=False
    )
    
    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()

class AprovacaoView(discord.ui.View):
    """Botões de aprovação/rejeição para financeiros"""
    
    def __init__(self, requisicao_id: str, tipo: str, usuario_id: int, valor: float, callback=None):
        super().__init__(timeout=3600)  # 1 hora
        self.requisicao_id = requisicao_id
        self.tipo = tipo  # 'saque' ou 'reembolso'
        self.usuario_id = usuario_id
        self.valor = valor
        self.callback = callback
    
    @discord.ui.button(label="✅ Aprovar", style=discord.ButtonStyle.green)
    async def aprovar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(FinanceiroModal())
        await self.callback(interaction, "approved", self.requisicao_id, self.tipo)
    
    @discord.ui.button(label="❌ Rejeitar", style=discord.ButtonStyle.red)
    async def rejeitar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(FinanceiroModal())
        await self.callback(interaction, "rejected", self.requisicao_id, self.tipo)

class Financeiro(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="adicionar-financeiro", description="Adiciona um usuário como financeiro (aprovador de saques/reembolsos)")
    @app_commands.describe(usuario="Usuário a adicionar como financeiro")
    async def adicionar_financeiro(self, interaction: discord.Interaction, usuario: discord.User):
        """Adiciona um financeiro com permissão para aprovar saques e reembolsos"""
        
        # Verificar se é admin
        if interaction.user.id != ADMIN_ID and not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Sem Permissão",
                description="Apenas administradores podem adicionar financeiros!",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Verificar se já é financeiro
        if is_financeiro(usuario.id):
            embed = discord.Embed(
                title="⚠️ Já é Financeiro",
                description=f"{usuario.mention} já tem permissão de financeiro!",
                color=discord.Color.yellow()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Adicionar financeiro
        if add_financeiro(usuario.id, interaction.user.id):
            embed = discord.Embed(
                title="✅ Financeiro Adicionado",
                description=f"{usuario.mention} agora pode aprovar saques e reembolsos!",
                color=discord.Color.green()
            )
            embed.add_field(name="Permissões", value="✓ Aprovar saques\n✓ Rejeitar saques\n✓ Aprovar reembolsos\n✓ Rejeitar reembolsos", inline=False)
            embed.add_field(name="Adicionado por", value=interaction.user.mention, inline=False)
            embed.set_thumbnail(url=usuario.avatar.url if usuario.avatar else None)
            
            await interaction.response.send_message(embed=embed, ephemeral=False)
            
            # Notificar o novo financeiro em DM
            try:
                dm_embed = discord.Embed(
                    title="🎖️ Você é Agora um Financeiro!",
                    description=f"Parabéns! {interaction.user.mention} te adicionou como **Financeiro**.\n\nVocê pode agora:\n✓ Aprovar saques\n✓ Rejeitar saques\n✓ Aprovar reembolsos\n✓ Rejeitar reembolsos\n\nAs requisições serão enviadas em seu privado para você revisar.",
                    color=discord.Color.gold()
                )
                await usuario.send(embed=dm_embed)
            except discord.Forbidden:
                pass
        else:
            embed = discord.Embed(
                title="❌ Erro",
                description="Erro ao adicionar financeiro!",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="remover-financeiro", description="Remove um usuário da lista de financeiros")
    @app_commands.describe(usuario="Usuário a remover")
    async def remover_financeiro(self, interaction: discord.Interaction, usuario: discord.User):
        """Remove um usuário de financeiro"""
        
        # Verificar se é admin
        if interaction.user.id != ADMIN_ID and not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Sem Permissão",
                description="Apenas administradores podem remover financeiros!",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Verificar se é financeiro
        if not is_financeiro(usuario.id):
            embed = discord.Embed(
                title="⚠️ Não é Financeiro",
                description=f"{usuario.mention} não é financeiro!",
                color=discord.Color.yellow()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Remover financeiro
        if remove_financeiro(usuario.id):
            embed = discord.Embed(
                title="✅ Financeiro Removido",
                description=f"{usuario.mention} não pode mais aprovar saques e reembolsos!",
                color=discord.Color.green()
            )
            embed.add_field(name="Removido por", value=interaction.user.mention, inline=False)
            
            await interaction.response.send_message(embed=embed, ephemeral=False)
            
            # Notificar o ex-financeiro em DM
            try:
                dm_embed = discord.Embed(
                    title="🔽 Permissão de Financeiro Removida",
                    description=f"Sua permissão de financeiro foi removida por {interaction.user.mention}.\n\nVocê não pode mais aprovar ou rejeitar saques e reembolsos.",
                    color=discord.Color.red()
                )
                await usuario.send(embed=dm_embed)
            except discord.Forbidden:
                pass
        else:
            embed = discord.Embed(
                title="❌ Erro",
                description="Erro ao remover financeiro!",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="listar-financeiros", description="Lista todos os financeiros")
    async def listar_financeiros(self, interaction: discord.Interaction):
        """Lista todos os usuários que são financeiros"""
        
        financeiros = get_all_financeiros()
        
        if not financeiros:
            embed = discord.Embed(
                title="📋 Nenhum Financeiro",
                description="Nenhum usuário foi adicionado como financeiro ainda!",
                color=discord.Color.blue()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        embed = discord.Embed(
            title="💰 Financeiros do Sistema",
            description=f"Total de {len(financeiros)} financeiro(s)",
            color=discord.Color.gold()
        )
        
        mensagem = ""
        for user_id in financeiros:
            try:
                user = await self.bot.fetch_user(user_id)
                info = get_financeiro_info(user_id)
                mensagem += f"• {user.mention} ({user.id})\n"
                if info and info['added_at']:
                    mensagem += f"  Adicionado em: {info['added_at'][:10]}\n"
            except:
                mensagem += f"• User ID: {user_id}\n"
        
        embed.add_field(name="Financeiros Ativos", value=mensagem, inline=False)
        embed.set_footer(text=f"Comandos de {interaction.user.name}", icon_url=interaction.user.avatar.url if interaction.user.avatar else None)
        
        await interaction.response.send_message(embed=embed, ephemeral=False)

async def setup(bot):
    await bot.add_cog(Financeiro(bot))
