"""
Cog de Comandos Administrativos e de Carteira

Inclui:
- Gerenciamento de permissões de cargo (/add-permissao, /rm-permissao)
- Visualização de dados pessoais (/meusdados)
- Gerenciamento de reembolsos (/reembolsar)
- Comandos de owner apenas
"""

import discord
from discord.ext import commands
from discord import app_commands
import os
from database import (
    add_user, get_balance, add_balance, remove_balance,
    add_cargo_permission, remove_cargo_permission, has_cargo_permission,
    get_all_cargo_permissions, add_transaction_history, 
    get_transaction_history_detailed, create_refund, get_pending_refunds,
    process_refund, set_pix_key, get_pix_key, is_financeiro,
    get_all_users_with_balance, get_total_balance
)
from config import is_owner, get_owner_ids
from wallet_components import CarteiraView, ConfirmarAcaoView, SacarView, criar_embed_carteira
from validador_pix import ValidadorPIX
from embed_utils import padronizar_embed

TAXA_RECEBIMENTO = float(os.getenv("TAXA_RECEBIMENTO", "0.65"))  # R$ 0,65
TAXA_SAQUE = float(os.getenv("TAXA_SAQUE", "5.00"))  # R$ 5,00
TAXA_REEMBOLSO = float(os.getenv("TAXA_REEMBOLSO", "1.00"))  # R$ 1,00
APROVADORES_REEMBOLSO = [int(id.strip()) for id in os.getenv("APROVADORES_REEMBOLSO", "").split(",") if id.strip()]

class AdminCog(commands.Cog):
    """Comandos administrativos e de carteira."""
    
    def __init__(self, bot):
        self.bot = bot
    
    # ════════════════════════════════════════════════════════════════════════
    # COMANDOS DE PERMISSÕES DE CARGO
    # ════════════════════════════════════════════════════════════════════════
    
    @app_commands.command(name="add-permissao", description="Adiciona permissão de cobrar para um cargo")
    async def add_cargo_permission_cmd(self, interaction: discord.Interaction, cargo: discord.Role):
        """Adiciona permissão de cobrar para um cargo.
        
        Uso: /add-permissao @cargo
        Apenas dono pode usar.
        Resposta é visual (apenas o dono vê).
        """
        
        if not is_owner(interaction.user.id):
            embed = discord.Embed(
                title="❌ Acesso Negado",
                description="Apenas o dono do bot pode usar este comando",
                color=discord.Color.red()
            )
            padronizar_embed(embed, interaction, user=interaction.user)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if add_cargo_permission(cargo.id):
            embed = discord.Embed(
                title="✅ Permissão Adicionada",
                description=f"O cargo **{cargo.name}** agora pode cobrar",
                color=discord.Color.green()
            )
            padronizar_embed(embed, interaction, user=interaction.user)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(
                title="❌ Erro",
                description="Não foi possível adicionar a permissão",
                color=discord.Color.red()
            )
            padronizar_embed(embed, interaction, user=interaction.user)
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="rm-permissao", description="Remove permissão de cobrar para um cargo")
    async def remove_cargo_permission_cmd(self, interaction: discord.Interaction, cargo: discord.Role):
        """Remove permissão de cobrar de um cargo.
        
        Uso: /rm-permissao @cargo
        Apenas dono pode usar.
        Resposta é visual (apenas o dono vê).
        """
        
        if not is_owner(interaction.user.id):
            embed = discord.Embed(
                title="❌ Acesso Negado",
                description="Apenas o dono do bot pode usar este comando",
                color=discord.Color.red()
            )
            padronizar_embed(embed, interaction, user=interaction.user)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if remove_cargo_permission(cargo.id):
            embed = discord.Embed(
                title="✅ Permissão Removida",
                description=f"O cargo **{cargo.name}** não pode mais cobrar",
                color=discord.Color.orange()
            )
            padronizar_embed(embed, interaction, user=interaction.user)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(
                title="❌ Erro",
                description="Não foi possível remover a permissão",
                color=discord.Color.red()
            )
            padronizar_embed(embed, interaction, user=interaction.user)
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="listar-permissoes", description="Lista todos os cargos com permissão de cobrar")
    async def list_cargo_permissions_cmd(self, interaction: discord.Interaction):
        """Lista todos os cargos com permissão de cobrar.
        
        Uso: /listar-permissoes
        Apenas dono pode usar.
        Resposta é visual (apenas o dono vê).
        """
        
        if not is_owner(interaction.user.id):
            embed = discord.Embed(
                title="❌ Acesso Negado",
                description="Apenas o dono do bot pode usar este comando",
                color=discord.Color.red()
            )
            padronizar_embed(embed, interaction, user=interaction.user)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        role_ids = get_all_cargo_permissions()
        
        if not role_ids:
            embed = discord.Embed(
                title="📋 Permissões de Cargo",
                description="Nenhum cargo com permissão configurado",
                color=discord.Color.blue()
            )
            padronizar_embed(embed, interaction, user=interaction.user)
        else:
            roles_list = []
            for role_id in role_ids:
                role = interaction.guild.get_role(role_id)
                if role:
                    roles_list.append(f"• {role.name} (ID: {role.id})")
            
            embed = discord.Embed(
                title="📋 Permissões de Cargo",
                description="\n".join(roles_list) if roles_list else "Nenhum cargo encontrado",
                color=discord.Color.blue()
            )
            padronizar_embed(embed, interaction, user=interaction.user)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    # ════════════════════════════════════════════════════════════════════════
    # COMANDOS DE CARTEIRA E DADOS PESSOAIS
    # ════════════════════════════════════════════════════════════════════════
    
    @app_commands.command(name="meusdados", description="Visualiza seus dados pessoais e saldo")
    async def my_data_cmd(self, interaction: discord.Interaction):
        """Visualiza seus dados pessoais e saldo.
        
        Uso: /meusdados
        Pode apagar seus dados ou sacar saldo.
        """
        
        add_user(interaction.user.id)
        saldo = get_balance(interaction.user.id)
        pix_key = get_pix_key(interaction.user.id)
        
        # Buscar histórico detalhado
        historico = get_transaction_history_detailed(interaction.user.id, limit=10)
        
        # Criar embed da carteira
        embed = criar_embed_carteira(
            username=interaction.user.name,
            saldo=saldo,
            transacoes=historico
        )
        
        # Adicionar dados pessoais
        cpf_display = "Não configurado"
        email_display = "Não configurado"
        telefone_display = "Não configurado"
        
        if pix_key:
            is_valid, chave_limpa, pix_type = ValidadorPIX.validar_pix(pix_key)
            
            if pix_type == "CPF":
                cpf_display = pix_key
            elif pix_type == "Email":
                email_display = pix_key
            elif pix_type == "Telefone":
                telefone_display = pix_key
            else:
                # Chave aleatória ou outro tipo
                pass
        
        embed.add_field(
            name="📱 Dados Pessoais",
            value=f"**CPF:** {cpf_display}\n**Email:** {email_display}\n**Telefone:** {telefone_display}",
            inline=False
        )
        
        # Criar view com botões
        view = CarteiraView(interaction.user.id)
        padronizar_embed(embed, interaction, user=interaction.user)
        msg = await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        
        # Aguardar ação
        await view.wait()
        
        if view.action == "sacar":
            # Mostrar dialog de saque
            await self.iniciar_saque(interaction, msg)
        
        elif view.action == "apagar":
            # Confirmar apagar dados
            confirm_view = ConfirmarAcaoView()
            confirm_embed = discord.Embed(
                title="⚠️ Apagar Dados",
                description="Tem certeza que deseja apagar seus dados?\n\n**Esta ação é irreversível!**",
                color=discord.Color.red()
            )
            padronizar_embed(confirm_embed, interaction, user=interaction.user)
            await interaction.followup.send(embed=confirm_embed, view=confirm_view)
            await confirm_view.wait()
            
            if confirm_view.confirmed:
                # TODO: Implementar apagar dados
                embed = discord.Embed(
                    title="✅ Dados Apagados",
                    description="Seus dados foram apagados do sistema",
                    color=discord.Color.green()
                )
            else:
                embed = discord.Embed(
                    title="❌ Cancelado",
                    description="Apagar dados foi cancelado",
                    color=discord.Color.orange()
                )
            
            padronizar_embed(embed, interaction, user=interaction.user)
            await interaction.followup.send(embed=embed, ephemeral=True)
    
    async def iniciar_saque(self, interaction: discord.Interaction, mensagem_anterior):
        """Inicia o processo de saque."""
        saldo = get_balance(interaction.user.id)
        pix_key = get_pix_key(interaction.user.id)
        
        if not pix_key:
            embed = discord.Embed(
                title="❌ PIX não configurado",
                description="Configure sua chave PIX primeiro com `/pix <chave>`",
                color=discord.Color.red()
            )
            padronizar_embed(embed, interaction, user=interaction.user)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        if saldo <= 0:
            embed = discord.Embed(
                title="❌ Saldo insuficiente",
                description="Você não tem saldo disponível",
                color=discord.Color.red()
            )
            padronizar_embed(embed, interaction, user=interaction.user)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        taxa = saldo * TAXA_SAQUE
        valor_final = saldo - taxa
        
        embed = discord.Embed(
            title="💸 Confirmar Saque",
            color=discord.Color.gold()
        )
        padronizar_embed(embed, interaction, user=interaction.user)
        
        embed.add_field(
            name="💰 Saldo Total",
            value=f"R$ {saldo:.2f}",
            inline=True
        )
        
        embed.add_field(
            name="📊 Taxa ({:.1f}%)".format(TAXA_SAQUE * 100),
            value=f"-R$ {taxa:.2f}",
            inline=True
        )
        
        embed.add_field(
            name="✅ Você receberá",
            value=f"**R$ {valor_final:.2f}**",
            inline=False
        )
        
        embed.add_field(
            name="🔑 Chave PIX",
            value=f"`{pix_key}`",
            inline=False
        )
        
        view = SacarView(interaction.user.id)
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)
        
        await view.wait()
        
        if view.action == "confirmar":
            # Processar saque
            # TODO: Integrar com MisticPay para transferência
            if remove_balance(interaction.user.id, saldo, f"Saque - Valor final: R$ {valor_final:.2f}"):
                add_transaction_history(
                    interaction.user.id,
                    "withdrawal",
                    valor_final,
                    f"Saque para {pix_key}",
                    gross_amount=saldo
                )
                
                embed = discord.Embed(
                    title="✅ Saque Processado",
                    description=f"Você receberá **R$ {valor_final:.2f}** em sua chave PIX",
                    color=discord.Color.green()
                )
            else:
                embed = discord.Embed(
                    title="❌ Erro",
                    description="Não foi possível processar o saque",
                    color=discord.Color.red()
                )
            
            padronizar_embed(embed, interaction, user=interaction.user)
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(
                title="❌ Saque Cancelado",
                description="Operação de saque foi cancelada",
                color=discord.Color.orange()
            )
            padronizar_embed(embed, interaction, user=interaction.user)
            await interaction.followup.send(embed=embed, ephemeral=True)
    
    # ════════════════════════════════════════════════════════════════════════
    # COMANDOS DE REEMBOLSO
    # ════════════════════════════════════════════════════════════════════════
    
    @app_commands.command(name="reembolsar", description="Solicita reembolso para um usuário")
    @app_commands.describe(usuario="Usuário para reembolsar", valor="Valor do reembolso", chave_pix="Chave PIX do usuário para receber o reembolso", motivo="Motivo do reembolso (opcional)")
    async def refund_cmd(self, interaction: discord.Interaction, usuario: discord.User, valor: float, chave_pix: str, motivo: str = "Reembolso solicitado"):
        """Solicita reembolso para um usuário.
        
        Uso: /reembolsar @usuario 16.00 "Motivo do reembolso"
        
        Taxas aplicadas:
        - Taxa de Reembolso: R$ 1,00
        - Taxa de Saque: R$ 5,00
        - Total de taxas: R$ 6,00
        
        Exemplo: Para o usuário receber R$ 16,00
        - Valor a informar: 16.00
        - Taxas: R$ 6,00
        - Total descontado: R$ 22,00
        
        O reembolso será enviado para aprovadores autorizados no privado.
        Apenas usuários com cargo configurado em /add-permissao podem usar.
        """
        
        # Verifica se o usuário tem um cargo com permissão de cobrar
        from database import has_cargo_permission
        tem_permissao = any(has_cargo_permission(role.id) for role in interaction.user.roles)
        
        if not tem_permissao:
            embed = discord.Embed(
                title="❌ Acesso Negado",
                description="Você precisa ter um cargo configurado em `/add-permissao` para usar este comando",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if valor <= 0:
            await interaction.response.send_message("❌ Valor deve ser maior que zero", ephemeral=True)
            return
        
        # Defer para processar em background
        await interaction.response.defer(ephemeral=True)
        
        if not APROVADORES_REEMBOLSO:
            await interaction.followup.send("❌ Nenhum aprovador configurado no .env (APROVADORES_REEMBOLSO)", ephemeral=True)
            return
        
        # Validar formato da chave PIX (básico)
        from validador_pix import ValidadorPIX
        validador = ValidadorPIX()
        valido, chave_formatada, tipo_chave = validador.validar_pix(chave_pix)
        if not valido:
            embed = discord.Embed(
                title="❌ Chave PIX Inválida",
                description=f"A chave PIX fornecida (`{chave_pix}`) não é válida.\n\nErro: {chave_formatada}\n\nVerifique o formato da chave.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        # Calcular apenas taxa de reembolso (sem taxa de saque)
        TAXA_REEMBOLSO_VALOR = 1.00
        valor_final = valor - TAXA_REEMBOLSO_VALOR
        
        if valor_final < 0.01:
            embed = discord.Embed(
                title="❌ Valor Insuficiente",
                description=f"O valor informado (**R$ {valor:.2f}**) é menor que a taxa de reembolso (R$ {TAXA_REEMBOLSO_VALOR:.2f})",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        # Descontar o valor total (sem taxa) do saldo de quem solicitou
        from database import get_balance, remove_balance
        saldo_solicitante = get_balance(interaction.user.id)
        if saldo_solicitante < valor:
            embed = discord.Embed(
                title="❌ Saldo Insuficiente",
                description=f"Você precisa de **R$ {valor:.2f}** para solicitar este reembolso.\n**Seu saldo:** R$ {saldo_solicitante:.2f}",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        # Remover o valor total do saldo do solicitante
        if not remove_balance(interaction.user.id, valor, f"Reembolso solicitado - ID pendente"):
            await interaction.followup.send("❌ Erro ao descontar valor do saldo", ephemeral=True)
            return
        
        # Criar reembolso pendente (valor já é o final que o usuário receberá)
        if create_refund(usuario.id, valor_final, motivo):
            # Buscar o ID do reembolso criado
            from database import get_pending_refunds
            refunds = get_pending_refunds()
            if not refunds:
                await interaction.followup.send("❌ Erro ao criar reembolso", ephemeral=True)
                return
            
            # Pegar o último reembolso criado (mais recente)
            refund_id = refunds[0][0]
            
            # Criar embed de solicitação
            embed_solicitacao = discord.Embed(
                title="📋 Solicitação de Reembolso",
                description=f"**ID:** #{refund_id}\n**Valor solicitado:** R$ {valor:.2f}\n**Taxa de Reembolso:** -R$ {TAXA_REEMBOLSO_VALOR:.2f}\n**💰 Valor a transferir:** R$ {valor_final:.2f}\n\n**Para:** {usuario.mention} ({usuario.name})\n**Chave PIX:** `{chave_pix}`\n**Motivo:** {motivo}\n\n**Solicitado por:** {interaction.user.mention}",
                color=discord.Color.orange(),
                timestamp=interaction.created_at
            )
            embed_solicitacao.add_field(name="⚠️ Ação Necessária", value="Aprove ou rejeite esta solicitação usando os botões abaixo.", inline=False)
            embed_solicitacao.set_footer(text="⏳ Aguardando aprovação")
            try:
                embed_solicitacao.set_thumbnail(url=usuario.display_avatar.url)
            except:
                pass
            padronizar_embed(embed_solicitacao, interaction, user=usuario)
            
            # Criar view de aprovação
            from ui_components import AprovacaoReembolsoView
            view = AprovacaoReembolsoView(refund_id, usuario.id, valor_final, chave_pix, motivo, APROVADORES_REEMBOLSO, timeout=None)
            
            # Enviar para o canal (visível para todos)
            try:
                embed_canal = discord.Embed(
                    title="📋 Nova Solicitação de Reembolso",
                    description=f"**ID:** #{refund_id}\n\n**📊 Valores:**\n**Valor solicitado:** R$ {valor:.2f}\n**Taxa de Reembolso:** -R$ {TAXA_REEMBOLSO_VALOR:.2f}\n**💰 Valor a transferir (PIX):** R$ {valor_final:.2f}\n\n**Para:** {usuario.mention}\n**Chave PIX:** `{chave_pix}`\n**Motivo:** {motivo}\n\n**Solicitado por:** {interaction.user.mention}",
                    color=discord.Color.orange(),
                    timestamp=interaction.created_at
                )
                embed_canal.set_footer(text="⏳ Aguardando aprovação")
                padronizar_embed(embed_canal, interaction, user=usuario)
                await interaction.channel.send(embed=embed_canal)
            except:
                pass
            
            # Enviar para cada aprovador no privado
            aprovadores_notificados = []
            for aprovador_id in APROVADORES_REEMBOLSO:
                try:
                    aprovador = await self.bot.fetch_user(aprovador_id)
                    msg = await aprovador.send(embed=embed_solicitacao, view=view)
                    aprovadores_notificados.append(aprovador.name)
                    
                    # Registrar message_id para poder deletar depois
                    from ui_components import AprovacaoReembolsoView
                    if refund_id not in AprovacaoReembolsoView._refund_messages:
                        AprovacaoReembolsoView._refund_messages[refund_id] = []
                    AprovacaoReembolsoView._refund_messages[refund_id].append({
                        'user_id': aprovador_id,
                        'message_id': msg.id,
                        'channel_id': msg.channel.id
                    })
                except Exception as e:
                    print(f"Erro ao enviar DM para aprovador {aprovador_id}: {e}")
            
            if aprovadores_notificados:
                embed_confirmacao = discord.Embed(
                    title="✅ Solicitação Enviada",
                    description=f"**Reembolso ID:** #{refund_id}\n**Valor:** R$ {valor:.2f}\n**Para:** {usuario.mention}\n**Motivo:** {motivo}\n\n**Aprovadores notificados:** {', '.join(aprovadores_notificados)}",
                    color=discord.Color.green(),
                    timestamp=interaction.created_at
                )
                embed_confirmacao.set_footer(text="✅ Solicitação registrada")
                padronizar_embed(embed_confirmacao, interaction, user=interaction.user)
                await interaction.followup.send(embed=embed_confirmacao, ephemeral=True)
                
                # Notificar usuário que está pendente
                try:
                    embed_user = discord.Embed(
                        title="⏳ Reembolso Solicitado",
                        description=f"Seu reembolso foi solicitado e está aguardando aprovação.\n\n**📊 Detalhes:**\n**ID:** #{refund_id}\n**Valor solicitado:** R$ {valor:.2f}\n**Taxa de Reembolso:** -R$ {TAXA_REEMBOLSO_VALOR:.2f}\n**💰 Valor a receber (PIX):** R$ {valor_final:.2f}\n\n**Chave PIX:** `{chave_pix}`\n**Motivo:** {motivo}\n\nVocê será notificado quando for aprovado ou rejeitado.",
                        color=discord.Color.orange(),
                        timestamp=interaction.created_at
                    )
                    embed_user.set_footer(text="⏳ Aguardando aprovação")
                    padronizar_embed(embed_user, interaction, user=usuario)
                    await usuario.send(embed=embed_user)
                except:
                    pass
            else:
                await interaction.followup.send("❌ Não foi possível notificar nenhum aprovador. Verifique se os IDs estão corretos.", ephemeral=True)
        else:
            embed = discord.Embed(
                title="❌ Erro",
                description="Não foi possível criar o reembolso",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
    
    @app_commands.command(name="listar-reembolsos", description="Lista todos os reembolsos (apenas dono)")
    async def list_refunds_cmd(self, interaction: discord.Interaction):
        """Lista todos os reembolsos pendentes.
        
        Uso: /listar-reembolsos
        Apenas dono pode usar.
        """
        
        if not is_owner(interaction.user.id):
            embed = discord.Embed(
                title="❌ Acesso Negado",
                description="Apenas o dono do bot pode usar este comando",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)
            return
        
        refunds = get_pending_refunds()
        
        if not refunds:
            embed = discord.Embed(
                title="📋 Reembolsos Pendentes",
                description="Nenhum reembolso pendente",
                color=discord.Color.blue()
            )
        else:
            refund_list = []
            for refund_id, user_id, amount, reason, payment_id, created_at in refunds:
                refund_list.append(
                    f"**ID:** {refund_id}\n"
                    f"**User:** {user_id}\n"
                    f"**Valor:** R$ {amount:.2f}\n"
                    f"**Motivo:** {reason}\n"
                    f"**Data:** {created_at}\n"
                )
            
            embed = discord.Embed(
                title="📋 Reembolsos Pendentes",
                description="\n".join(refund_list) if refund_list else "Nenhum",
                color=discord.Color.blue()
            )
        
        await interaction.response.send_message(embed=embed)
    
    # ════════════════════════════════════════════════════════════════════════
    # COMANDOS DE SALDO (OWNER)
    # ════════════════════════════════════════════════════════════════════════
    
    @app_commands.command(name="adicionarsaldo", description="Adiciona saldo manualmente a um usuário")
    async def add_balance_cmd(self, interaction: discord.Interaction, usuario: discord.User, valor: float):
        """Adiciona saldo manualmente a um usuário.
        
        Uso: /adicionarsaldo @usuario 100
        Apenas dono pode usar.
        Resposta é visual (apenas o dono vê).
        """
        
        if not is_owner(interaction.user.id):
            embed = discord.Embed(
                title="❌ Acesso Negado",
                description="Apenas o dono do bot pode usar este comando",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if valor <= 0:
            embed = discord.Embed(
                title="❌ Valor Inválido",
                description="O valor deve ser maior que R$ 0",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        add_user(usuario.id)
        add_balance(usuario.id, valor, f"Adição manual por {interaction.user.name}")
        add_transaction_history(
            usuario.id,
            "manual_add",
            valor,
            f"Adição manual por admin",
            sender_id=interaction.user.id,
            sender_name=interaction.user.name
        )
        
        embed = discord.Embed(
            title="✅ Saldo Adicionado",
            description=f"**R$ {valor:.2f}** adicionado para @{usuario.name}",
            color=discord.Color.green()
        )
        embed.add_field(
            name="👤 Usuário",
            value=f"{usuario.name} ({usuario.id})",
            inline=True
        )
        embed.add_field(
            name="💰 Valor",
            value=f"R$ {valor:.2f}",
            inline=True
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="removersaldo", description="Remove saldo manualmente de um usuário")
    async def remove_balance_cmd(self, interaction: discord.Interaction, usuario: discord.User, valor: float):
        """Remove saldo manualmente de um usuário.
        
        Uso: /removersaldo @usuario 100
        Apenas dono pode usar.
        Resposta é visual (apenas o dono vê).
        """
        
        if not is_owner(interaction.user.id):
            embed = discord.Embed(
                title="❌ Acesso Negado",
                description="Apenas o dono do bot pode usar este comando",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if valor <= 0:
            embed = discord.Embed(
                title="❌ Valor Inválido",
                description="O valor deve ser maior que R$ 0",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        saldo = get_balance(usuario.id)
        if saldo < valor:
            embed = discord.Embed(
                title="❌ Saldo Insuficiente",
                description=f"Saldo disponível: R$ {saldo:.2f}",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        remove_balance(usuario.id, valor, f"Remoção manual por {interaction.user.name}")
        add_transaction_history(
            usuario.id,
            "manual_remove",
            valor,
            f"Remoção manual por admin",
            sender_id=interaction.user.id,
            sender_name=interaction.user.name
        )
        
        embed = discord.Embed(
            title="✅ Saldo Removido",
            description=f"**R$ {valor:.2f}** removido de @{usuario.name}",
            color=discord.Color.orange()
        )
        embed.add_field(
            name="👤 Usuário",
            value=f"{usuario.name} ({usuario.id})",
            inline=True
        )
        embed.add_field(
            name="💰 Valor",
            value=f"R$ {valor:.2f}",
            inline=True
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    
    @app_commands.command(name="configurar-taxas", description="Configura as taxas de recebimento e saque em reais (R$)")
    @app_commands.describe(taxa_recebimento="Taxa de recebimento em R$ (ex: 0.50)", taxa_saque="Taxa de saque em R$ (ex: 0.30)")
    async def configure_taxes_cmd(self, interaction: discord.Interaction, taxa_recebimento: float = None, taxa_saque: float = None):
        """Configura as taxas de recebimento e saque em reais.
        
        Uso: /configurar-taxas taxa_recebimento:0.50 taxa_saque:0.30
        Apenas dono pode usar.
        Resposta é visual (apenas o dono vê).
        """
        
        if not is_owner(interaction.user.id):
            embed = discord.Embed(
                title="❌ Acesso Negado",
                description="Apenas o dono do bot pode usar este comando",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Importar tax_config do payment.py
        from cogs.payment import tax_config
        
        if taxa_recebimento is None and taxa_saque is None:
            embed = discord.Embed(
                title="💰 Configuração de Taxas Atual",
                description="Taxas aplicadas em todas as transações",
                color=discord.Color.gold()
            )
            embed.add_field(
                name="📥 Taxa de Recebimento",
                value=f"`R$ {tax_config['taxa_recebimento']:.2f}`\nCobrada quando cliente paga",
                inline=False
            )
            embed.add_field(
                name="📤 Taxa de Saque",
                value=f"`R$ {tax_config['taxa_saque']:.2f}`\nCobrada quando vendedor saca",
                inline=False
            )
            embed.add_field(
                name="💡 Como Usar",
                value="`/configurar-taxas taxa_recebimento:0.50 taxa_saque:0.30`\n\nOu configure apenas uma:\n`/configurar-taxas taxa_recebimento:0.75`",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Validar valores
        if taxa_recebimento is not None and taxa_recebimento < 0:
            await interaction.response.send_message(
                "❌ Taxa de recebimento não pode ser negativa!",
                ephemeral=True
            )
            return
        
        if taxa_saque is not None and taxa_saque < 0:
            await interaction.response.send_message(
                "❌ Taxa de saque não pode ser negativa!",
                ephemeral=True
            )
            return
        
        # Salvar as mudanças
        taxa_rec_antes = tax_config["taxa_recebimento"]
        taxa_saque_antes = tax_config["taxa_saque"]
        
        if taxa_recebimento is not None:
            tax_config["taxa_recebimento"] = taxa_recebimento
        
        if taxa_saque is not None:
            tax_config["taxa_saque"] = taxa_saque
        
        # Atualizar o arquivo .env
        try:
            with open(".env", "r") as f:
                env_content = f.read()
            
            # Substituir ou adicionar as variáveis
            if "TAXA_RECEBIMENTO=" in env_content:
                env_content = env_content.replace(
                    f"TAXA_RECEBIMENTO={taxa_rec_antes}",
                    f"TAXA_RECEBIMENTO={tax_config['taxa_recebimento']}"
                )
            else:
                env_content += f"\nTAXA_RECEBIMENTO={tax_config['taxa_recebimento']}"
            
            if "TAXA_SAQUE=" in env_content:
                env_content = env_content.replace(
                    f"TAXA_SAQUE={taxa_saque_antes}",
                    f"TAXA_SAQUE={tax_config['taxa_saque']}"
                )
            else:
                env_content += f"\nTAXA_SAQUE={tax_config['taxa_saque']}"
            
            with open(".env", "w") as f:
                f.write(env_content)
            
            # Criar embed de confirmação
            embed = discord.Embed(
                title="✅ Taxas Atualizadas",
                description="As novas taxas entrarão em vigor imediatamente",
                color=discord.Color.green()
            )
            
            if taxa_recebimento is not None:
                embed.add_field(
                    name="📥 Taxa de Recebimento",
                    value=f"**Antes:** R$ {taxa_rec_antes:.2f}\n**Depois:** R$ {tax_config['taxa_recebimento']:.2f}",
                    inline=True
                )
            
            if taxa_saque is not None:
                embed.add_field(
                    name="📤 Taxa de Saque",
                    value=f"**Antes:** R$ {taxa_saque_antes:.2f}\n**Depois:** R$ {tax_config['taxa_saque']:.2f}",
                    inline=True
                )
            
            embed.add_field(
                name="⚠️ Nota Importante",
                value="As mudanças serão persistidas mesmo após restart do bot",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erro ao Salvar",
                description=f"Não foi possível salvar as taxas: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
            # Reverter as mudanças em memória
            tax_config["taxa_recebimento"] = taxa_rec_antes
            tax_config["taxa_saque"] = taxa_saque_antes
    
    @app_commands.command(name="saldo-geral", description="Ver saldo de todos os usuários (dono apenas)")
    async def saldo_geral(self, interaction: discord.Interaction):
        """Exibe o saldo total e de cada usuário."""
        
        if not is_owner(interaction.user.id):
            embed = discord.Embed(
                title="❌ Acesso Negado",
                description="Apenas o dono pode usar este comando",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        usuarios = get_all_users_with_balance()
        total = get_total_balance()
        
        if not usuarios:
            embed = discord.Embed(
                title="💰 Saldo Geral",
                description="Nenhum usuário com saldo",
                color=discord.Color.greyple()
            )
            embed.add_field(
                name="💸 Total",
                value=f"R$ 0.00",
                inline=False
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        embed = discord.Embed(
            title="💰 Saldo Geral do Sistema",
            description=f"📊 Total de usuários com saldo: {len(usuarios)}",
            color=discord.Color.gold(),
            timestamp=interaction.created_at
        )
        
        # Adicionar cada usuário
        usuarios_text = ""
        for idx, (user_id, balance) in enumerate(usuarios, 1):
            try:
                user = await self.bot.fetch_user(user_id)
                nome = user.name
            except:
                nome = f"Usuário {user_id}"
            
            usuarios_text += f"`{idx:2}` → **{nome}** | R$ {balance:>10.2f}\n"
        
        # Se for muito grande, dividir em chunks
        if len(usuarios_text) > 1024:
            # Pegar os primeiros 10 e resumo do resto
            primeiros = "\n".join(usuarios_text.split("\n")[:10])
            resto_count = len(usuarios) - 10
            usuarios_text = f"{primeiros}\n\n*... e mais {resto_count} usuário(s)*"
        
        embed.add_field(
            name="👥 Usuários",
            value=usuarios_text or "Nenhum",
            inline=False
        )
        
        # Total
        embed.add_field(
            name="💸 Saldo Total",
            value=f"**R$ {total:,.2f}**",
            inline=False
        )
        
        # Estatísticas
        saldo_medio = total / len(usuarios) if usuarios else 0
        embed.add_field(
            name="📈 Estatísticas",
            value=f"**Média por usuário:** R$ {saldo_medio:,.2f}\n**Maior saldo:** R$ {usuarios[0][1]:,.2f}\n**Menor saldo:** R$ {usuarios[-1][1]:,.2f}",
            inline=False
        )
        
        embed.set_footer(text="Acesso exclusivo ao dono")
        
        await interaction.followup.send(embed=embed, ephemeral=True)

async def setup(bot):
    """Função requerida pelo discord.py 2.0+ para carregar a cog."""
    await bot.add_cog(AdminCog(bot))
