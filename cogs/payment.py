import discord
from discord.ext import commands
from discord import app_commands
import os
from io import BytesIO
import base64
from dotenv import load_dotenv
from database import (
    get_balance, get_total_balance, add_balance, 
    remove_balance, withdraw_balance, get_transaction_history, 
    add_user, set_pix_key, get_pix_key, get_balance_by_user,
    register_payment, has_cargo_permission
)
from payment_handler import MisticPayHandler
from ui_components import PagamentoView
from validador_pix import ValidadorPIX
from embed_utils import padronizar_embed

OWNER_ID = int(os.getenv("OWNER_ID", "0"))
VENDEDOR_ROLE_ID = int(os.getenv("VENDEDOR_ROLE_ID", "0"))

# Dicionário para armazenar taxas (permite mudança em runtime)
tax_config = {
    "taxa_recebimento": float(os.getenv("TAXA_RECEBIMENTO", "0.65")),
    "taxa_saque": float(os.getenv("TAXA_SAQUE", "5.00"))
}

# Variáveis para backward compatibility
TAXA_RECEBIMENTO = tax_config["taxa_recebimento"]
TAXA_SAQUE = tax_config["taxa_saque"]
APROVADORES_REEMBOLSO = [int(id.strip()) for id in os.getenv("APROVADORES_REEMBOLSO", "").split(",") if id.strip()]

# Emojis para notificações
EMOJI_SUCESSO = os.getenv("EMOJI_SUCESSO", "✅")
EMOJI_CLIENTE = os.getenv("EMOJI_CLIENTE", "👥")
EMOJI_VENDEDOR = os.getenv("EMOJI_VENDEDOR", "👤")
EMOJI_VALOR = os.getenv("EMOJI_VALOR", "💰")
EMOJI_PAGAMENTO = os.getenv("EMOJI_PAGAMENTO", "💳")

class PagamentoViewClienteOnly(discord.ui.View):
    """View com botão de pagamento que só o cliente pode clicar."""
    
    def __init__(self, cliente_id: int, pix_code: str, qr_code_base64: str = None):
        super().__init__(timeout=3600)  # 1 hora
        self.cliente_id = cliente_id
        self.pix_code = pix_code
        self.qr_code_base64 = qr_code_base64
    
    @discord.ui.button(label="💳 Pagar Agora", style=discord.ButtonStyle.success, custom_id="btn_pagar")
    async def btn_pagar(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Botão para cliente obter código PIX."""
        
        if interaction.user.id != self.cliente_id:
            await interaction.response.send_message(
                "❌ Apenas o cliente mencionado pode usar este botão!",
                ephemeral=True
            )
            return
        
        # Calcular tempo de expiração (29 minutos)
        from datetime import datetime, timedelta
        agora = datetime.now()
        expira_em = agora + timedelta(minutes=29)
        tempo_expiracao = f"<t:{int(expira_em.timestamp())}:R>"  # Formato Discord relativo
        
        # Enviar código PIX puro (SEM markdown de link)
        embed = discord.Embed(
            title="💳 Código PIX Copia e Cola",
            description="**Copie o código abaixo:**",
            color=discord.Color.green(),
            timestamp=interaction.created_at
        )
        embed.add_field(
            name="📱 Como pagar",
            value="1️⃣ Copie o código (enviado logo abaixo)\n2️⃣ Abra seu app de banco\n3️⃣ Escolha **PIX Copia e Cola**\n4️⃣ Cole o código e confirme",
            inline=False
        )
        embed.add_field(
            name="⏱️ Tempo de Processamento",
            value="Geralmente alguns segundos\nMáximo 5 minutos",
            inline=False
        )
        embed.add_field(
            name="⏳ Código PIX Expira",
            value=f"Válido por 29 minutos\nExpira {tempo_expiracao}",
            inline=False
        )
        embed.set_footer(text="✅ Pagamento será confirmado automaticamente")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Enviar código PIX separadamente em mensagem de texto puro para facilitar cópia
        await interaction.followup.send(f"{self.pix_code}", ephemeral=True)
        
        # Enviar QR Code se disponível
        if self.qr_code_base64:
            try:
                qr_base64 = self.qr_code_base64
                if qr_base64.startswith('data:image'):
                    qr_base64 = qr_base64.split(',')[1]
                qr_data = base64.b64decode(qr_base64)
                file = discord.File(
                    BytesIO(qr_data),
                    filename="qr_code.png"
                )
                
                embed_qr = discord.Embed(
                    title="📱 QR Code PIX",
                    description="Escaneie com a câmera do seu app de banco",
                    color=discord.Color.blue(),
                    timestamp=interaction.created_at
                )
                embed_qr.add_field(
                    name="⏳ Válido por",
                    value=f"29 minutos\nExpira {tempo_expiracao}",
                    inline=False
                )
                embed_qr.set_footer(text="Escaneie rápido para pagar com PIX")
                
                await interaction.followup.send(embed=embed_qr, file=file, ephemeral=True)
            except Exception as e:
                print(f"Erro ao enviar QR code: {e}")

class PaymentCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.payment_handler = MisticPayHandler()
    
    def is_vendedor(self, user: discord.User, guild: discord.Guild = None):
        """Verifica se o usuário é vendedor (tem o cargo ou é dono)."""
        if user.id == OWNER_ID:
            return True
        if VENDEDOR_ROLE_ID > 0 and guild is not None:
            member = guild.get_member(user.id)
            if member:
                role = discord.utils.get(member.roles, id=VENDEDOR_ROLE_ID)
                return role is not None
        return False
    
    @app_commands.command(name="pix", description="Define sua chave PIX (CPF, Email, Telefone ou Chave aleatória)")
    async def set_pix(self, interaction: discord.Interaction, pix_key: str):
        """Define sua chave PIX (CPF, Email, Telefone ou Chave aleatória).
        
        Resposta é visual (apenas você vê).
        ⚠️ Aviso: Verifique cuidadosamente a chave PIX!
        Não nos responsabilizamos por erros de digitação.
        """
        add_user(interaction.user.id)
        
        # Validar PIX
        valido, chave_limpa, tipo = ValidadorPIX.validar_pix(pix_key)
        
        if not valido:
            embed = discord.Embed(
                title="❌ PIX Inválido",
                description=chave_limpa,  # chave_limpa contém a mensagem de erro
                color=discord.Color.red()
            )
            embed.add_field(
                name="📋 Formatos aceitos",
                value="**CPF:** 000.000.000-00 ou 00000000000\n" +
                      "**Email:** seu@email.com\n" +
                      "**Telefone:** (11) 9 1234-5678 ou 11991234567\n" +
                      "**Chave Aleatória:** 32 caracteres hexadecimais",
                inline=False
            )
            padronizar_embed(embed, interaction, user=interaction.user)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Criar embed de confirmação
        embed_confirm = discord.Embed(
            title="⚠️ Confirme sua Chave PIX",
            description=f"**Tipo:** {tipo}\n**Chave:** `{chave_limpa}`\n\n⚠️ Verifique cuidadosamente antes de confirmar!",
            color=discord.Color.orange()
        )
        padronizar_embed(embed_confirm, interaction, user=interaction.user, footer="Confirme para continuar")
        
        # Criar botões de confirmação
        from ui_components import PixConfirmView
        view = PixConfirmView(interaction.user.id, chave_limpa)
        
        await interaction.response.send_message(embed=embed_confirm, view=view, ephemeral=True)
        await view.wait()
        
        if not view.confirmado:
            return
        
        # Salvar PIX após confirmação
        set_pix_key(interaction.user.id, chave_limpa)
        
        embed = discord.Embed(
            title="✅ Chave PIX Salva",
            color=discord.Color.green()
        )
        embed.add_field(name="📌 Tipo", value=tipo, inline=True)
        embed.add_field(name="🔑 Chave", value=f"`{chave_limpa}`", inline=True)
        embed.add_field(
            name="⚠️ AVISO IMPORTANTE",
            value="Verifique cuidadosamente a chave acima.\n**Não nos responsabilizamos por erros de digitação ou chaves incorretas.**",
            inline=False
        )
        embed.set_footer(text="Você pode sacar para esta chave quando desejar")
        padronizar_embed(embed, interaction, user=interaction.user)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="saldo", description="Mostra seu saldo pessoal")
    async def get_personal_balance(self, interaction: discord.Interaction):
        """Mostra seu saldo pessoal.
        
        Resposta é visual (apenas você vê).
        """
        add_user(interaction.user.id)
        balance = get_balance(interaction.user.id)
        
        from embed_utils import criar_separador, formatar_valor
        
        embed = discord.Embed(
            title="💰 Seu Saldo",
            description=f"{criar_separador('SALDO DISPONÍVEL')}\n{formatar_valor(balance)}",
            color=discord.Color.green(),
            timestamp=interaction.created_at
        )
        
        # Adicionar informações extras
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
        
        # Adicionar botões de ação rápida se for vendedor ou dono
        from ui_components import SaldoActionView
        view = SaldoActionView(interaction.user.id, balance, self.is_vendedor(interaction.user, interaction.guild))
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @app_commands.command(name="historico", description="Mostra seu histórico de transações")
    async def transaction_history(self, interaction: discord.Interaction):
        """Mostra seu histórico de transações."""
        add_user(interaction.user.id)
        history = get_transaction_history(interaction.user.id, limit=10)
        
        if not history:
            embed = discord.Embed(
                title="📜 Histórico de Transações",
                description="Nenhuma transação encontrada.\n\nRealize vendas ou transações para ver seu histórico aqui.",
                color=discord.Color.purple()
            )
            padronizar_embed(embed, interaction, user=interaction.user, icone_tipo="history")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        from embed_utils import criar_separador
        
        embed = discord.Embed(
            title="📜 Histórico de Transações",
            description=f"{criar_separador('ÚLTIMAS TRANSAÇÕES')}",
            color=discord.Color.purple(),
            timestamp=interaction.created_at
        )
        padronizar_embed(embed, interaction, user=interaction.user, icone_tipo="history")
        
        for idx, (tipo, amount, description, created_at) in enumerate(history, 1):
            emoji = "➕" if tipo == "add" else "➖"
            valor_formatado = f"+R$ {amount:.2f}" if tipo == "add" else f"-R$ {amount:.2f}"
            
            embed.add_field(
                name=f"{emoji} {idx}. {description}",
                value=f"`{valor_formatado}` • {created_at}",
                inline=False
            )
        
        # Adicionar rodapé informativo
        embed.add_field(
            name=f"\n{criar_separador()}",
            value="💡 *Mostrando até 10 transações mais recentes*",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="cobrar", description="Cria um link de pagamento com QR Code")
    @app_commands.choices(repassar_taxa=[
        app_commands.Choice(name="Sim - Cliente paga a taxa", value="sim"),
        app_commands.Choice(name="Não - Vendedor absorve a taxa", value="nao")
    ])
    @app_commands.describe(
        cliente="Usuário para cobrar",
        valor="Valor da cobrança",
        repassar_taxa="Repassar taxa ao cliente?"
    )
    async def create_payment_link(self, interaction: discord.Interaction, cliente: discord.User, valor: float, repassar_taxa: str):
        """Cria um link de pagamento com QR Code e botão de pagamento."""
        
        try:
            # Verificar limite máximo de transação
            valor_maximo = float(os.getenv("VALOR_MAXIMO_TRANSACAO", "10000"))
            if valor > valor_maximo:
                embed = discord.Embed(
                    title="❌ Valor Excede o Limite",
                    description=f"O valor de **R$ {valor:.2f}** excede o limite máximo de **R$ {valor_maximo:.2f}** por transação.",
                    color=discord.Color.red()
                )
                padronizar_embed(embed, interaction, user=interaction.user)
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Verificar permissão: é vendedor, tem role vendedor, ou é o dono
            is_allowed = False
            
            # Se OWNER_ID está configurado, verificar se é dono
            if OWNER_ID > 0 and interaction.user.id == OWNER_ID:
                is_allowed = True
            # Se VENDEDOR_ROLE_ID está configurado e em um servidor, verificar role
            elif VENDEDOR_ROLE_ID > 0 and interaction.guild:
                member = interaction.guild.get_member(interaction.user.id)
                if member and discord.utils.get(member.roles, id=VENDEDOR_ROLE_ID):
                    is_allowed = True
            # Se nenhum está configurado, permitir qualquer um usar
            elif OWNER_ID == 0 and VENDEDOR_ROLE_ID == 0:
                is_allowed = True
            
            if not is_allowed:
                embed = discord.Embed(
                    title="❌ Acesso Negado",
                    description=f"Você não tem permissão para usar este comando.\nApenas vendedores ou o dono podem cobrar.",
                    color=discord.Color.red()
                )
                padronizar_embed(embed, interaction, user=interaction.user)
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            if valor <= 0:
                await interaction.response.send_message("❌ O valor deve ser maior que R$ 0.", ephemeral=True)
                return
            
            # Validar repassar_taxa
            repassar_taxa_lower = repassar_taxa.lower().strip()
            if repassar_taxa_lower not in ["sim", "s", "nao", "n", "não"]:
                await interaction.response.send_message("❌ `repassar_taxa` deve ser 'sim' ou 'não'", ephemeral=True)
                return
            
            repassar_taxa = repassar_taxa_lower in ["sim", "s"]
            
            add_user(interaction.user.id)
            add_user(cliente.id)
            
            # Calcular taxas (tax_config["taxa_recebimento"] é um valor fixo em reais, não porcentagem)
            if repassar_taxa:
                taxa_valor = tax_config["taxa_recebimento"]
                total = valor + taxa_valor
                mensagem_taxa = f"+ R$ {taxa_valor:.2f} (Taxa - Repassada ao cliente)"
            else:
                taxa_valor = tax_config["taxa_recebimento"]
                total = valor  # Cliente paga apenas o valor, taxa é descontada do vendedor
                mensagem_taxa = f"- R$ {taxa_valor:.2f} (Taxa - Descontada do vendedor)"
            
            # Mostrar mensagem de carregamento animada
            await interaction.response.defer()
            loading_embed = discord.Embed(
                title="⏳ Processando...",
                description="```\n⠋ Gerando link de pagamento...\n⠙ Criando QR Code...\n⠹ Configurando taxa...\n```",
                color=discord.Color.orange()
            )
            loading_msg = await interaction.followup.send(embed=loading_embed)
            
            try:
                result = self.payment_handler.create_payment_link(
                    cliente.id, 
                    total,
                    f"Cobrança de {interaction.user.name}",
                    channel_id=interaction.channel.id
                )
            except Exception as e:
                print(f"Erro ao criar link de pagamento: {e}")
                import traceback
                traceback.print_exc()
                result = None
            
            if result is None:
                embed_erro = discord.Embed(
                    title="❌ Erro ao Gerar Cobrança",
                    description="Não foi possível gerar o link de pagamento. Tente novamente mais tarde.",
                    color=discord.Color.red(),
                    timestamp=interaction.created_at
                )
                embed_erro.add_field(
                    name="ℹ️ Detalhes",
                    value="Erro ao conectar com o serviço de pagamento",
                    inline=False
                )
                embed_erro.set_footer(text="Tente novamente em instantes")
                padronizar_embed(embed_erro, interaction, user=interaction.user)
                await loading_msg.delete()
                await interaction.followup.send(embed=embed_erro)
                return
            
            from embed_utils import criar_separador, formatar_valor
            
            # Criar embed detalhado com PIX copia e cola
            embed = discord.Embed(
                title="💳 Cobrança de Serviço",
                description=f"{criar_separador('FATURA GERADA')}",
                color=discord.Color.gold(),
                timestamp=interaction.created_at
            )
            
            embed.add_field(
                name="👤 Vendedor",
                value=interaction.user.mention,
                inline=True
            )
            
            embed.add_field(
                name="👥 Cliente",
                value=cliente.mention,
                inline=True
            )
            
            embed.add_field(
                name="\u200b",
                value="\u200b",
                inline=False
            )
            
            embed.add_field(
                name="📋 Valor do Serviço",
                value=f"`R$ {valor:.2f}`",
                inline=True
            )
            
            embed.add_field(
                name="📊 Taxas",
                value=mensagem_taxa,
                inline=True
            )
            
            embed.add_field(
                name="\u200b",
                value="\u200b",
                inline=False
            )
            
            embed.add_field(
                name="💰 Total a Pagar",
                value=formatar_valor(total),
                inline=False
            )
            
            embed.add_field(
                name="📌 ID da Cobrança",
                value=f"`{result['payment_id']}`",
                inline=False
            )
            
            embed.set_footer(text="💡 Clique no botão para obter o código PIX | Válido por 1 hora")
            
            padronizar_embed(embed, interaction, user=cliente, icone_tipo="payment")
            
            # Registrar pagamento no banco com canal e ID interno da MisticPay
            register_payment(
                payment_id=result['payment_id'],
                receiver_id=interaction.user.id,  # CORREÇÃO: receiver é o vendedor, não o cliente
                amount=total,
                channel_id=interaction.channel.id,
                internal_id=result.get('internal_id')  # ID interno da MisticPay (ex: 505520)
            )
            
            await loading_msg.delete()
            
            # Criar view com botão "Pagar Agora"
            view = PagamentoViewClienteOnly(
                cliente_id=cliente.id,
                pix_code=result['url'],
                qr_code_base64=result.get('qr_code_base64')
            )
            
            # Enviar embed COM botão
            msg = await interaction.followup.send(embed=embed, view=view)
        
        except Exception as e:
            print(f"Erro geral no /cobrar: {e}")
            import traceback
            traceback.print_exc()
            
            embed_erro = discord.Embed(
                title="❌ Erro Inesperado",
                description="Ocorreu um erro ao processar a cobrança",
                color=discord.Color.red(),
                timestamp=interaction.created_at
            )
            embed_erro.add_field(
                name="⚠️ Detalhes",
                value=f"```{str(e)[:200]}```",
                inline=False
            )
            embed_erro.set_footer(text="Se persistir, contate o suporte")
            padronizar_embed(embed_erro, interaction, user=interaction.user)
            
            try:
                loading_msg.delete()
            except:
                pass
            
            try:
                await interaction.followup.send(embed=embed_erro)
            except:
                await interaction.response.send_message(embed=embed_erro, ephemeral=True)
    
    @app_commands.command(name="sacar", description="Saca saldo para sua chave PIX (dono e vendedores)")
    @app_commands.describe(amount="Valor a sacar (deixe em branco para sacar tudo)")
    async def withdraw(self, interaction: discord.Interaction, amount: float = None):
        """Saca saldo para sua chave PIX (dono e vendedores) com confirmacao."""
        
        # Verificar se é o dono ou vendedor
        is_owner = interaction.user.id == OWNER_ID
        is_seller = any(has_cargo_permission(role.id) for role in interaction.user.roles) if not is_owner else True
        
        if not is_owner and not is_seller:
            embed = discord.Embed(
                title="❌ Acesso Negado",
                description=f"Apenas donos e vendedores podem sacar.",
                color=discord.Color.red()
            )
            padronizar_embed(embed, interaction, user=interaction.user)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        add_user(interaction.user.id)
        
        # Se não informar valor, saca tudo
        saldo_atual = get_balance(interaction.user.id)
        if amount is None:
            amount = saldo_atual
        
        if amount <= 0:
            await interaction.response.send_message("❌ Saldo insuficiente ou valor inválido.", ephemeral=True)
            return
        
        # Calcular taxa de saque (tax_config["taxa_saque"] é um valor fixo, não porcentagem)
        taxa_saque_valor = tax_config["taxa_saque"]
        total_saque = amount - taxa_saque_valor  # Taxa é descontada do saque
        
        # Verificar se tem saldo suficiente
        if saldo_atual < amount:
            await interaction.response.send_message(f"❌ Saldo insuficiente. Você tem R$ {saldo_atual:.2f}", ephemeral=True)
            return
        
        pix_key = get_pix_key(interaction.user.id)
        if not pix_key:
            embed = discord.Embed(
                title="❌ PIX não configurado",
                description="Use `/pix <sua_chave_pix>` para configurar sua chave PIX.",
                color=discord.Color.red()
            )
            padronizar_embed(embed, interaction, user=interaction.user)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # CONFIRMAÇÃO EM 2 PASSOS
        from ui_components import ConfirmarView
        from embed_utils import criar_separador, formatar_valor
        
        embed_confirma = discord.Embed(
            title="⚠️ Confirmação de Saque",
            description=f"{criar_separador('CONFIRME OS DADOS')}",
            color=discord.Color.orange(),
            timestamp=interaction.created_at
        )
        
        embed_confirma.add_field(
            name="💰 Valor a Sacar",
            value=f"`R$ {amount:.2f}`",
            inline=True
        )
        
        embed_confirma.add_field(
            name="📊 Taxa de Saque",
            value=f"`- R$ {taxa_saque_valor:.2f}`",
            inline=True
        )
        
        embed_confirma.add_field(
            name="\u200b",
            value="\u200b",
            inline=False
        )
        
        embed_confirma.add_field(
            name="💸 Você Receberá",
            value=formatar_valor(total_saque),
            inline=False
        )
        
        embed_confirma.add_field(
            name="🔑 Chave PIX",
            value=f"`{pix_key}`",
            inline=False
        )
        
        embed_confirma.add_field(
            name="\u200b",
            value=f"{criar_separador()}",
            inline=False
        )
        
        embed_confirma.add_field(
            name="⚠️ Atenção",
            value="Verifique cuidadosamente sua chave PIX antes de confirmar!",
            inline=False
        )
        
        padronizar_embed(embed_confirma, interaction, user=interaction.user, icone_tipo="warning")
        
        view = ConfirmarView()
        await interaction.response.send_message(embed=embed_confirma, view=view, ephemeral=True)
        msg = await interaction.original_response()
        
        # Aguardar confirmação
        await view.wait()
        
        if view.resultado is None:
            embed_cancelado = discord.Embed(
                title="⏱️ Saque Cancelado",
                description="Tempo expirado para confirmação",
                color=discord.Color.greyple()
            )
            padronizar_embed(embed_cancelado, interaction, user=interaction.user)
            await msg.edit(embed=embed_cancelado, view=None)
            return
        
        if not view.resultado:
            embed_cancelado = discord.Embed(
                title="❌ Saque Cancelado",
                description="Você cancelou o saque",
                color=discord.Color.red()
            )
            padronizar_embed(embed_cancelado, interaction, user=interaction.user)
            await msg.edit(embed=embed_cancelado, view=None)
            return
        
        # DEBITAR SALDO IMEDIATAMENTE (bloqueado para aprovação)
        saldo_atual = get_balance(interaction.user.id)
        
        if saldo_atual < amount:
            embed_saldo = discord.Embed(
                title="❌ Saldo Insuficiente",
                description=f"Seu saldo mudou. Você tem R$ {saldo_atual:.2f}",
                color=discord.Color.red()
            )
            padronizar_embed(embed_saldo, interaction, user=interaction.user)
            await msg.edit(embed=embed_saldo, view=None)
            return
        
        # Debitar o saldo (fica bloqueado até aprovação)
        if not remove_balance(interaction.user.id, amount, f"Saque solicitado - Aguardando aprovação"):
            embed_erro = discord.Embed(
                title="❌ Erro ao Bloquear Saldo",
                description="Erro ao processar o saque",
                color=discord.Color.red()
            )
            padronizar_embed(embed_erro, interaction, user=interaction.user)
            await msg.edit(embed=embed_erro, view=None)
            return
        
        # ENVIAR PARA APROVAÇÃO NO PRIVADO DO DONO
        loading_embed = discord.Embed(
            title="⏳ Processando Saque...",
            description="```\n⠋ Verificando saldo...\n⠙ Bloqueando valor...\n⠹ Enviando para aprovação...\n```",
            color=discord.Color.orange()
        )
        from embed_utils import padronizar_embed as pad_embed
        pad_embed(loading_embed, interaction, icone_tipo="pending")
        loading_msg = await interaction.followup.send(embed=loading_embed, ephemeral=True)
        
        from embed_utils import criar_separador, formatar_valor, criar_barra_progresso
        
        # Criar embed de solicitação
        embed_aprovacao = discord.Embed(
            title="💸 Solicitação de Saque",
            description=f"{criar_separador('NOVA SOLICITAÇÃO')}\n\n{criar_barra_progresso(50)}\n*Aguardando aprovação...*",
            color=discord.Color.blue(),
            timestamp=interaction.created_at
        )
        
        embed_aprovacao.add_field(
            name="👤 Solicitante",
            value=f"{interaction.user.mention}\n`{interaction.user.name}#{interaction.user.discriminator}`",
            inline=False
        )
        
        embed_aprovacao.add_field(
            name="💰 Valor Solicitado",
            value=f"`R$ {amount:.2f}`",
            inline=True
        )
        
        embed_aprovacao.add_field(
            name="📊 Taxa de Saque",
            value=f"`- R$ {taxa_saque_valor:.2f}`",
            inline=True
        )
        
        embed_aprovacao.add_field(
            name="\u200b",
            value="\u200b",
            inline=False
        )
        
        embed_aprovacao.add_field(
            name="💸 Valor a Transferir",
            value=formatar_valor(total_saque),
            inline=False
        )
        
        embed_aprovacao.add_field(
            name="🔑 Chave PIX",
            value=f"`{pix_key}`",
            inline=False
        )
        
        padronizar_embed(embed_aprovacao, interaction, user=interaction.user, icone_tipo="pending")
        
        # Criar view de aprovação de saque sem timeout
        from ui_components import AprovacaoSaqueView
        from database import get_all_financeiros
        
        view_aprovacao = AprovacaoSaqueView(interaction.user.id, amount, total_saque, pix_key, self.payment_handler, timeout=None)
        
        # Enviar para o dono e todos os financeiros no privado
        aprovadores_notificados = []
        try:
            # Enviar para o dono
            if OWNER_ID > 0:
                owner = await self.bot.fetch_user(OWNER_ID)
                msg = await owner.send(embed=embed_aprovacao, view=view_aprovacao)
                view_aprovacao.message = msg
                aprovadores_notificados.append(owner.name)
                
                # Registrar message_id para poder deletar depois
                if interaction.user.id not in AprovacaoSaqueView._withdrawal_messages:
                    AprovacaoSaqueView._withdrawal_messages[interaction.user.id] = []
                AprovacaoSaqueView._withdrawal_messages[interaction.user.id].append({
                    'user_id': OWNER_ID,
                    'message_id': msg.id,
                    'channel_id': msg.channel.id
                })
            
            # Enviar para todos os financeiros
            financeiros = get_all_financeiros()
            for financeiro in financeiros:
                try:
                    financeiro_user = await self.bot.fetch_user(financeiro['user_id'])
                    msg = await financeiro_user.send(embed=embed_aprovacao, view=view_aprovacao)
                    aprovadores_notificados.append(financeiro_user.name)
                    
                    # Registrar message_id para poder deletar depois
                    if interaction.user.id not in AprovacaoSaqueView._withdrawal_messages:
                        AprovacaoSaqueView._withdrawal_messages[interaction.user.id] = []
                    AprovacaoSaqueView._withdrawal_messages[interaction.user.id].append({
                        'user_id': financeiro['user_id'],
                        'message_id': msg.id,
                        'channel_id': msg.channel.id
                    })
                except Exception as e:
                    print(f"Erro ao enviar saque para financeiro {financeiro['user_id']}: {e}")
        except Exception as e:
            print(f"Erro ao enviar saque para aprovação: {e}")
            # Devolver saldo se falhar ao enviar
            from database import add_balance
            add_balance(interaction.user.id, amount)
        
        embed_pendente = discord.Embed(
            title="⏳ Saque em Análise",
            description=f"{criar_separador('AGUARDANDO APROVAÇÃO')}\n\n{criar_barra_progresso(33)}\n*Seu saque foi enviado para aprovação*",
            color=discord.Color.orange(),
            timestamp=interaction.created_at
        )
        
        embed_pendente.add_field(
            name="💰 Valor Bloqueado",
            value=formatar_valor(amount),
            inline=True
        )
        
        embed_pendente.add_field(
            name="💸 Você Receberá",
            value=formatar_valor(total_saque),
            inline=True
        )
        
        embed_pendente.add_field(
            name="\u200b",
            value="\u200b",
            inline=False
        )
        
        embed_pendente.add_field(
            name="⏱️ Status Atual",
            value="🔒 Saldo debitado e bloqueado\n⏳ Aguardando aprovação do financeiro",
            inline=False
        )
        
        embed_pendente.add_field(
            name="ℹ️ Importante",
            value="• Se aprovado: PIX enviado automaticamente\n• Se rejeitado: Saldo devolvido automaticamente\n• Você será notificado em ambos os casos",
            inline=False
        )
        
        padronizar_embed(embed_pendente, interaction, user=interaction.user, icone_tipo="pending")
        
        await loading_msg.delete()
        await interaction.followup.send(embed=embed_pendente, ephemeral=True)
    
    # COMANDOS APENAS PARA DONO

async def setup(bot):
    """Função requerida pelo discord.py 2.0+ para carregar a cog."""
    await bot.add_cog(PaymentCog(bot))
