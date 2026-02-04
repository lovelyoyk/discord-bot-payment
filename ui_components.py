import discord
import time
from typing import Callable, Optional
from database import get_balance, set_pix_key
from embed_utils import padronizar_embed

class PagamentoView(discord.ui.View):
    """View com botão de pagamento"""
    def __init__(self, url: str, timeout: int = 3600):
        super().__init__(timeout=timeout)
        self.url = url
    
    @discord.ui.button(label="Pagar Agora", style=discord.ButtonStyle.green, emoji="💳")
    async def pagar_agora(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Botão que abre o link de pagamento"""
        embed = discord.Embed(
            title="💳 Link de Pagamento",
            description=f"[👉 Clique aqui para pagar 👈]({self.url})",
            color=discord.Color.green()
        )
        embed.set_footer(text="Você será redirecionado para o pagamento")
        padronizar_embed(embed, interaction, user=interaction.user)
        await interaction.response.send_message(embed=embed, ephemeral=True)

class ConfirmarView(discord.ui.View):
    """View com botões de Sim e Não"""
    def __init__(self, timeout: int = 300):
        super().__init__(timeout=timeout)
        self.resultado = None
    
    @discord.ui.button(label="Sim", style=discord.ButtonStyle.green, emoji="✅")
    async def sim(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.resultado = True
        await interaction.response.defer()
        self.stop()
    
    @discord.ui.button(label="Não", style=discord.ButtonStyle.red, emoji="❌")
    async def nao(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.resultado = False
        await interaction.response.defer()
        self.stop()

class SaqueButton(discord.ui.Button):
    """Botão de saque rápido"""
    def __init__(self, user_id: int):
        super().__init__(label="Sacar Saldo", style=discord.ButtonStyle.green, emoji="💸")
        self.user_id = user_id
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Este botão não é para você!", ephemeral=True)
            return
        
        balance = get_balance(self.user_id)
        if balance <= 0:
            await interaction.response.send_message("❌ Você não tem saldo para sacar.", ephemeral=True)
            return
        
        await interaction.response.send_message(
            f"💸 Use o comando `/sacar {balance:.2f}` para sacar todo seu saldo.",
            ephemeral=True
        )

class SaldoActionView(discord.ui.View):
    """View com botões de ação rápida no saldo"""
    def __init__(self, user_id: int, balance: float, is_vendedor: bool):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.balance = balance
        
        # Só adiciona botões se for vendedor e tiver saldo
        if is_vendedor and balance > 0:
            self.add_item(discord.ui.Button(
                label="💸 Sacar",
                style=discord.ButtonStyle.green,
                custom_id="sacar",
                emoji="💸"
            ))
        
        # Adiciona botão de histórico sempre
        self.add_item(discord.ui.Button(
            label="📊 Histórico",
            style=discord.ButtonStyle.primary,
            custom_id="historico",
            emoji="📜"
        ))
        
        # Adiciona botão de atualizar
        self.add_item(discord.ui.Button(
            label="🔄 Atualizar",
            style=discord.ButtonStyle.secondary,
            custom_id="atualizar",
            emoji="🔄"
        ))
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Este botão não é para você!", ephemeral=True)
            return False
        
        custom_id = interaction.data.get("custom_id", "")
        
        if custom_id == "sacar":
            await interaction.response.send_message(
                f"💸 Use o comando `/sacar {self.balance:.2f}` para sacar seu saldo.",
                ephemeral=True
            )
        elif custom_id == "historico":
            await interaction.response.send_message(
                "📜 Use o comando `/historico` para ver suas transações.",
                ephemeral=True
            )
        elif custom_id == "atualizar":
            from embed_utils import criar_separador, formatar_valor, padronizar_embed
            balance = get_balance(self.user_id)
            self.balance = balance
            
            embed = discord.Embed(
                title="💰 Seu Saldo",
                description=f"{criar_separador('SALDO DISPONÍVEL')}\n{formatar_valor(balance)}",
                color=discord.Color.green()
            )
            
            if balance > 0:
                embed.add_field(
                    name="📊 Status",
                    value="✅ Saldo disponível para saque",
                    inline=True
                )
                if balance >= 10:
                    embed.add_field(
                        name="💸 Saque Mínimo",
                        value="R$ 10,00",
                        inline=True
                    )
            else:
                embed.add_field(
                    name="ℹ️ Informação",
                    value="Realize vendas para acumular saldo",
                    inline=False
                )
            
            padronizar_embed(embed, interaction, user=interaction.user, icone_tipo="money")
            await interaction.response.edit_message(embed=embed, view=self)
        
        return True

class PixConfirmView(discord.ui.View):
    """View de confirmação de chave PIX"""
    def __init__(self, user_id: int, chave_pix: str, timeout: int = 300):
        super().__init__(timeout=timeout)
        self.user_id = user_id
        self.chave_pix = chave_pix
        self.confirmado = False
    
    @discord.ui.button(label="Confirmar", style=discord.ButtonStyle.green, emoji="✅")
    async def confirmar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Este botão não é para você!", ephemeral=True)
            return
        
        self.confirmado = True
        embed = discord.Embed(
            title="✅ Chave PIX Confirmada",
            description=f"Sua chave PIX foi salva com sucesso!\\n\\n**Chave:** `{self.chave_pix}`",
            color=discord.Color.green()
        )
        padronizar_embed(embed, interaction, user=interaction.user)
        await interaction.response.edit_message(embed=embed, view=None)
        self.stop()
    
    @discord.ui.button(label="Cancelar", style=discord.ButtonStyle.red, emoji="❌")
    async def cancelar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Este botão não é para você!", ephemeral=True)
            return
        
        self.confirmado = False
        embed = discord.Embed(
            title="❌ Cancelado",
            description="A configuração da chave PIX foi cancelada.\\n\\nUse `/pix` novamente para tentar outra vez.",
            color=discord.Color.red()
        )
        padronizar_embed(embed, interaction, user=interaction.user)
        await interaction.response.edit_message(embed=embed, view=None)
        self.stop()
    
    @discord.ui.button(label="Alterar", style=discord.ButtonStyle.gray, emoji="🔄")
    async def alterar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Este botão não é para você!", ephemeral=True)
            return
        
        self.confirmado = False
        embed = discord.Embed(
            title="🔄 Digite Novamente",
            description="Use o comando `/pix` com a chave correta.",
            color=discord.Color.blue()
        )
        padronizar_embed(embed, interaction, user=interaction.user)
        await interaction.response.edit_message(embed=embed, view=None)
        self.stop()

class MenuView(discord.ui.View):
    """View com menu de seleção"""
    def __init__(self, opcoes: dict, timeout: int = 300):
        super().__init__(timeout=timeout)
        self.opcoes = opcoes
        self.resultado = None
        
        for label, valor in list(opcoes.items())[:5]:  # Discord permite máx 5 botões
            self.add_item(
                discord.ui.Button(
                    label=label,
                    style=discord.ButtonStyle.primary,
                    custom_id=str(valor)
                )
            )
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        self.resultado = interaction.data['custom_id']
        await interaction.response.defer()
        self.stop()
        return True

class AprovacaoReembolsoView(discord.ui.View):
    """View para aprovação/rejeição de reembolsos"""
    _processing_refunds = {}  # Proteção contra concorrência
    _refund_messages = {}  # Armazena message_ids para cada refund_id
    
    def __init__(self, refund_id: int, user_id: int, amount: float, pix_key: str, reason: str, aprovador_ids: list, timeout: int = None):
        super().__init__(timeout=timeout)
        self.refund_id = refund_id
        self.user_id = user_id
        self.amount = amount
        self.pix_key = pix_key
        self.reason = reason
        self.aprovador_ids = aprovador_ids
        self.aprovado = None
        self.aprovador_id = None
        self.processado = False
        
        # Inicializar lista de mensagens para este reembolso
        if refund_id not in self._refund_messages:
            self._refund_messages[refund_id] = []
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Verifica se o usuário tem permissão para aprovar"""
        if interaction.user.id not in self.aprovador_ids:
            await interaction.response.send_message(
                "❌ Você não tem permissão para aprovar/rejeitar este reembolso!",
                ephemeral=True
            )
            return False
        return True
    
    @discord.ui.button(label="Aprovar Reembolso", style=discord.ButtonStyle.green, emoji="✅")
    async def aprovar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        
        try:
            # Verificar se já está sendo processado
            if self.refund_id in self._processing_refunds:
                await interaction.followup.send("⚠️ Este reembolso já está sendo processado", ephemeral=True)
                return
            
            # Marcar como em processamento
            self._processing_refunds[self.refund_id] = True
            
            from database import approve_refund, add_transaction_history
            from payment_handler import MisticPayHandler
            
            # Aprovar no banco
            if not approve_refund(self.refund_id, interaction.user.id):
                await interaction.followup.send("❌ Erro ao aprovar reembolso (banco).", ephemeral=True)
                return
            
            # Fazer transferência PIX via API MisticPay
            result = MisticPayHandler.create_withdrawal(self.user_id, self.amount, self.pix_key)
            
            if result:
                # Transferência aceita (status retornado pela API)
                status_pix = result.get("status", "QUEUED")
                if str(status_pix).upper() == "QUEUED":
                    status_pix = "Aprovado"
                add_transaction_history(
                    self.user_id,
                    'reembolso',
                    self.amount,
                    self.amount,
                    f"Reembolso aprovado e transferido - {self.reason}",
                    None,
                    None,
                    f"REFUND_{self.refund_id}"
                )
                
                self.processado = True
                self.aprovado = True
                self.aprovador_id = interaction.user.id
                
                embed = discord.Embed(
                    title="✅ Reembolso Aprovado e Transferido",
                    description=f"**ID:** #{self.refund_id}\n**Valor:** R$ {self.amount:.2f}\n**Usuário:** <@{self.user_id}>\n**Chave PIX:** `{self.pix_key}`\n**Motivo:** {self.reason}\n\n**Status:** {status_pix}\n**Aprovado por:** {interaction.user.mention}",
                    color=discord.Color.green(),
                    timestamp=interaction.created_at
                )
                embed.set_footer(text="✅ Reembolso aprovado")
                await interaction.edit_original_response(embed=embed, view=None)
                
                # Deletar mensagens antigas de todos os aprovadores
                if self.refund_id in self._refund_messages:
                    for msg_info in self._refund_messages[self.refund_id]:
                        try:
                            user_id = msg_info.get('user_id')
                            message_id = msg_info.get('message_id')
                            channel_id = msg_info.get('channel_id')
                            
                            # Tentar deletar a mensagem
                            user = await interaction.client.fetch_user(user_id)
                            channel = user.dm_channel
                            if channel:
                                try:
                                    msg = await channel.fetch_message(message_id)
                                    await msg.delete()
                                except:
                                    pass
                        except:
                            pass
                    
                    # Limpar lista de mensagens
                    del self._refund_messages[self.refund_id]
                
                # Notificar usuário
                try:
                    user = await interaction.client.fetch_user(self.user_id)
                    embed_user = discord.Embed(
                        title="✅ Reembolso Aprovado e Transferido",
                        description=f"Seu reembolso de **R$ {self.amount:.2f}** foi aprovado e enviado via PIX!\n\n**Chave PIX:** `{self.pix_key}`\n**Motivo:** {self.reason}\n**Status:** {status_pix}\n\nO valor deve chegar em alguns minutos.",
                        color=discord.Color.green(),
                        timestamp=interaction.created_at
                    )
                    embed_user.set_footer(text="✅ Reembolso aprovado")
                    await user.send(embed=embed_user)
                except:
                    pass
                
                self.stop()
            else:
                # Erro na transferência
                embed = discord.Embed(
                    title="❌ Erro na Transferência",
                    description=f"**ID:** #{self.refund_id}\n**Erro:** Falha na conexão com API\n\nO reembolso foi aprovado no sistema, mas a transferência PIX falhou.",
                    color=discord.Color.red(),
                    timestamp=interaction.created_at
                )
                embed.set_footer(text="⚠️ Verifique a API e tente novamente")
                await interaction.edit_original_response(embed=embed, view=None)
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            await interaction.followup.send(f"❌ Erro ao processar reembolso: {str(e)}", ephemeral=True)
        finally:
            # Liberar lock
            if self.refund_id in self._processing_refunds:
                del self._processing_refunds[self.refund_id]
    
    @discord.ui.button(label="Rejeitar Reembolso", style=discord.ButtonStyle.red, emoji="❌")
    async def rejeitar(self, interaction: discord.Interaction, button: discord.ui.Button):
        from database import reject_refund
        
        # Rejeitar no banco
        if reject_refund(self.refund_id, interaction.user.id):
            self.aprovado = False
            self.aprovador_id = interaction.user.id
            
            embed = discord.Embed(
                title="❌ Reembolso Rejeitado",
                description=f"**Valor:** R$ {self.amount:.2f}\n**Usuário:** <@{self.user_id}>\n**Motivo:** {self.reason}\n\n**Rejeitado por:** {interaction.user.mention}",
                color=discord.Color.red(),
                timestamp=interaction.created_at
            )
            embed.set_footer(text="❌ Reembolso rejeitado")
            await interaction.response.edit_message(embed=embed, view=None)
            
            # Notificar usuário
            try:
                user = await interaction.client.fetch_user(self.user_id)
                embed_user = discord.Embed(
                    title="❌ Reembolso Rejeitado",
                    description=f"Seu reembolso de **R$ {self.amount:.2f}** foi rejeitado.\n\n**Motivo:** {self.reason}",
                    color=discord.Color.red(),
                    timestamp=interaction.created_at
                )
                embed_user.set_footer(text="❌ Reembolso rejeitado")
                await user.send(embed=embed_user)
            except:
                pass
            
            self.stop()
        else:
            await interaction.response.send_message("❌ Erro ao rejeitar reembolso.", ephemeral=True)

class RejeitarSaqueModal(discord.ui.Modal):
    def __init__(self, view: "AprovacaoSaqueView"):
        super().__init__(title="Rejeitar Saque")
        self.view = view
        self.motivo = discord.ui.TextInput(
            label="Motivo da rejeição",
            style=discord.TextStyle.paragraph,
            max_length=300,
            required=True
        )
        self.add_item(self.motivo)

    async def on_submit(self, interaction: discord.Interaction):
        await self.view._finalizar_rejeicao(interaction, str(self.motivo))


class AprovacaoSaqueView(discord.ui.View):
    """View para aprovação de saques com proteção contra concorrência"""
    # Dicionário para rastrear saques em processamento (lock)
    _processing_withdrawals = {}
    # Cooldown por aprovador (5s entre ações)
    _approver_last_action = {}
    # Armazena message_ids para cada user_id (saque)
    _withdrawal_messages = {}
    
    def __init__(self, user_id: int, amount: float, amount_final: float, pix_key: str, payment_handler, timeout: int = None):
        super().__init__(timeout=timeout)
        self.user_id = user_id
        self.amount = amount
        self.amount_final = amount_final
        self.pix_key = pix_key
        self.payment_handler = payment_handler
        self.processado = False
        self.message: Optional[discord.Message] = None
        
        # Inicializar lista de mensagens para este saque
        if user_id not in self._withdrawal_messages:
            self._withdrawal_messages[user_id] = []

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Aplica cooldown de 5s entre aprovações/rejeições por aprovador."""
        now = time.time()
        last_action = self._approver_last_action.get(interaction.user.id, 0)
        if now - last_action < 5:
            await interaction.response.send_message(
                "⏳ Aguarde 5 segundos entre uma aprovação e outra.",
                ephemeral=True
            )
            return False
        self._approver_last_action[interaction.user.id] = now
        return True
    
    async def on_timeout(self):
        """Chamado quando o timeout expira (se houver)"""
        # Devolver saldo se expirar
        try:
            from database import add_balance
            if not self.processado:
                add_balance(self.user_id, self.amount)
                print(f"⏱️ Saque expirado para {self.user_id} - Saldo devolvido")
        except Exception as e:
            print(f"Erro ao devolver saldo no timeout: {e}")
    
    @discord.ui.button(label="Aprovar Saque", style=discord.ButtonStyle.green, emoji="✅")
    async def aprovar(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            from database import get_balance, add_balance
            
            # PROTEÇÃO CONTRA CONCORRÊNCIA: verificar se já está em processamento
            if self.user_id in self._processing_withdrawals:
                embed = discord.Embed(
                    title="⚠️ Saque em Processamento",
                    description="Este saque já está sendo processado. Aguarde um momento.",
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Marcar como em processamento
            self._processing_withdrawals[self.user_id] = True
            
            try:
                # Verificar saldo antes de processar
                saldo_atual = get_balance(self.user_id)
                if saldo_atual < 0:
                    # Saldo foi debitado, agora é negativo - erro raro
                    embed = discord.Embed(
                        title="❌ Erro no Saldo",
                        description=f"Saldo inconsistente. Saque cancelado.",
                        color=discord.Color.red()
                    )
                    await interaction.response.edit_message(embed=embed, view=None)
                    # Devolver saldo
                    add_balance(self.user_id, self.amount)
                    return
                
                # Processar saque na API MisticPay
                result = self.payment_handler.create_withdrawal(self.user_id, self.amount_final, self.pix_key)
                
                if result:
                    # SUCESSO! Não precisa devolver saldo pois já foi debitado
                    self.processado = True
                    
                    from embed_utils import criar_separador, formatar_valor, padronizar_embed
                    
                    embed = discord.Embed(
                        title="✅ Saque Aprovado e Processado",
                        description=f"{criar_separador('SAQUE APROVADO')}\n@{interaction.user.mention} aprovou o saque",
                        color=discord.Color.green(),
                        timestamp=interaction.created_at
                    )
                    
                    embed.add_field(
                        name="👤 Solicitante",
                        value=f"<@{self.user_id}>",
                        inline=True
                    )
                    
                    embed.add_field(
                        name="👨‍💼 Aprovado por",
                        value=interaction.user.mention,
                        inline=True
                    )
                    
                    embed.add_field(
                        name="\u200b",
                        value="\u200b",
                        inline=False
                    )
                    
                    embed.add_field(
                        name="💰 Valor Solicitado",
                        value=f"`R$ {self.amount:.2f}`",
                        inline=True
                    )
                    
                    embed.add_field(
                        name="📊 Taxa de Saque",
                        value=f"`- R$ {(self.amount - self.amount_final):.2f}`",
                        inline=True
                    )
                    
                    embed.add_field(
                        name="\u200b",
                        value="\u200b",
                        inline=False
                    )
                    
                    embed.add_field(
                        name="💸 Valor Transferido",
                        value=f"**{formatar_valor(self.amount_final)}**",
                        inline=False
                    )
                    
                    embed.add_field(
                        name="🔑 Chave PIX",
                        value=f"`{self.pix_key}`",
                        inline=False
                    )
                    
                    embed.add_field(
                        name="📌 ID do Saque",
                        value=f"`{result['payout_id']}`",
                        inline=True
                    )
                    
                    status_saque = result.get("status", "QUEUED")
                    if str(status_saque).upper() == "QUEUED":
                        status_saque = "Aprovado"
                    
                    embed.add_field(
                        name="⏱️ Status",
                        value=f"✅ {status_saque}",
                        inline=True
                    )
                    
                    padronizar_embed(embed, interaction, icone_tipo="success")
                    await interaction.response.edit_message(embed=embed, view=None)
                    
                    # Notificar usuário com menção
                    try:
                        user = await interaction.client.fetch_user(self.user_id)
                        
                        embed_user = discord.Embed(
                            title="✅ Saque Aprovado",
                            description=f"{criar_separador('TRANSFERÊNCIA APROVADA')}\n\n{user.mention}, seu saque foi aprovado com sucesso!",
                            color=discord.Color.green(),
                            timestamp=interaction.created_at
                        )
                        
                        embed_user.add_field(
                            name="💸 Valor a Receber",
                            value=formatar_valor(self.amount_final),
                            inline=False
                        )
                        
                        embed_user.add_field(
                            name="🔑 Chave PIX",
                            value=f"`{self.pix_key}`",
                            inline=False
                        )
                        
                        embed_user.add_field(
                            name="📌 Código de Rastreio",
                            value=f"`{result['payout_id']}`",
                            inline=False
                        )
                        
                        embed_user.add_field(
                            name="⏱️ Previsão",
                            value="O valor deve chegar em alguns minutos",
                            inline=False
                        )
                        
                        padronizar_embed(embed_user, interaction, icone_tipo="success")
                        await user.send(content=f"{user.mention}", embed=embed_user)
                    except:
                        pass
                    
                    # Deletar mensagens antigas de aprovação
                    if self.user_id in self._withdrawal_messages:
                        for msg_info in self._withdrawal_messages[self.user_id]:
                            try:
                                user_id = msg_info.get('user_id')
                                message_id = msg_info.get('message_id')
                                
                                # Tentar deletar a mensagem
                                user_owner = await interaction.client.fetch_user(user_id)
                                channel = user_owner.dm_channel
                                if channel:
                                    try:
                                        msg = await channel.fetch_message(message_id)
                                        await msg.delete()
                                    except:
                                        pass
                            except:
                                pass
                        
                        # Limpar lista de mensagens
                        del self._withdrawal_messages[self.user_id]
                    
                    self.stop()
                else:
                    # ERRO NA API: devolver saldo
                    add_balance(self.user_id, self.amount)
                    
                    embed = discord.Embed(
                        title="❌ Erro ao Processar Saque",
                        description="Erro ao processar o saque na API MisticPay. Saldo foi devolvido ao usuário.",
                        color=discord.Color.red(),
                        timestamp=interaction.created_at
                    )
                    embed.set_footer(text="⚠️ Verifique a API e tente novamente")
                    await interaction.response.edit_message(embed=embed, view=None)
                    
                    # Notificar usuário
                    try:
                        user = await interaction.client.fetch_user(self.user_id)
                        embed_user = discord.Embed(
                            title="⚠️ Saque Cancelado - Erro",
                            description=f"Seu saque de **R$ {self.amount_final:.2f}** não pode ser processado. Seu saldo foi devolvido.",
                            color=discord.Color.orange(),
                            timestamp=interaction.created_at
                        )
                        embed_user.set_footer(text="Saldo devolvido")
                        await user.send(embed=embed_user)
                    except:
                        pass
            finally:
                # Remover lock
                if self.user_id in self._processing_withdrawals:
                    del self._processing_withdrawals[self.user_id]
        
        except Exception as e:
            print(f"Erro ao aprovar saque: {e}")
            import traceback
            traceback.print_exc()
            
            # Devolver saldo em caso de erro não tratado
            try:
                from database import add_balance
                add_balance(self.user_id, self.amount)
            except:
                pass
            
            await interaction.response.send_message(f"❌ Erro ao aprovar saque: {str(e)}", ephemeral=True)
    
    @discord.ui.button(label="Rejeitar Saque", style=discord.ButtonStyle.red, emoji="❌")
    async def rejeitar(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = RejeitarSaqueModal(self)
        await interaction.response.send_modal(modal)

    async def _finalizar_rejeicao(self, interaction: discord.Interaction, motivo: str):
        try:
            from database import add_balance

            if not self.processado:
                # Devolver o saldo (foi debitado no início)
                add_balance(self.user_id, self.amount)
                self.processado = True

            embed = discord.Embed(
                title="❌ Saque Rejeitado",
                description="O saque foi rejeitado. O saldo foi devolvido ao usuário.",
                color=discord.Color.red(),
                timestamp=interaction.created_at
            )
            embed.set_footer(text="❌ Saque rejeitado")

            embed.add_field(
                name="💰 Valor Devolvido",
                value=f"R$ {self.amount:.2f}",
                inline=False
            )

            embed.add_field(
                name="📝 Motivo",
                value=motivo,
                inline=False
            )

            embed.add_field(
                name="ℹ️ Observação",
                value="O saldo foi reintegrado à conta do usuário",
                inline=False
            )

            if self.message:
                await self.message.edit(embed=embed, view=None)
                await interaction.response.send_message("✅ Saque rejeitado com sucesso.", ephemeral=True)
            else:
                await interaction.response.edit_message(embed=embed, view=None)

            # Notificar usuário
            try:
                user = await interaction.client.fetch_user(self.user_id)
                embed_user = discord.Embed(
                    title="❌ Saque Rejeitado",
                    description=f"Seu saque de **R$ {self.amount:.2f}** foi rejeitado. O saldo foi devolvido à sua conta.\n\n**Motivo:** {motivo}",
                    color=discord.Color.red(),
                    timestamp=interaction.created_at
                )
                embed_user.set_footer(text="Saldo devolvido")
                await user.send(embed=embed_user)
            except:
                pass

            self.stop()
        except Exception as e:
            print(f"Erro ao rejeitar saque: {e}")
            await interaction.response.send_message(f"❌ Erro ao rejeitar saque: {str(e)}", ephemeral=True)

