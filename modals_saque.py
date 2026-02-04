"""
Modals para saque de saldo
"""

import discord
from database import get_balance


class ModalConfirmarSaqueTudo(discord.ui.Modal, title="💸 Confirmar Saque de Todo Saldo"):
    """Modal para confirmar saque de todo o saldo"""
    
    def __init__(self, user_id: int, balance: float):
        super().__init__()
        self.user_id = user_id
        self.amount = balance
    
    async def on_submit(self, interaction: discord.Interaction):
        """Processa o saque de todo o saldo"""
        try:
            # Importar a função de saque
            from cogs.payment import PaymentCog
            from config import OWNER_ID
            
            # Encontrar a instância do PaymentCog
            payment_cog = None
            for cog in interaction.client.cogs.values():
                if cog.__class__.__name__ == 'PaymentCog':
                    payment_cog = cog
                    break
            
            if not payment_cog:
                await interaction.response.send_message("❌ Erro ao processar saque.", ephemeral=True)
                return
            
            # Chamar a função withdraw sem amount (sacar tudo)
            await payment_cog.withdraw(interaction, amount=None)
        
        except Exception as e:
            print(f"[MODAL] Erro em ModalConfirmarSaqueTudo: {e}")
            await interaction.response.send_message(f"❌ Erro ao processar: {str(e)}", ephemeral=True)


class ModalEscolherValorSaque(discord.ui.Modal, title="💰 Escolher Valor"):
    """Modal para escolher o valor a sacar"""
    
    def __init__(self, user_id: int, balance: float):
        super().__init__()
        self.user_id = user_id
        self.balance = balance
        
        self.valor_input = discord.ui.TextInput(
            label="Valor a Sacar (R$)",
            placeholder=f"Ex: 10.50 (máximo: R$ {balance:.2f})",
            required=True,
            min_length=1,
            max_length=10
        )
        self.add_item(self.valor_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        """Processa a entrada do valor"""
        try:
            # Validar e converter o valor
            valor_str = self.valor_input.value.strip().replace(",", ".")
            amount = float(valor_str)
            
            if amount <= 0:
                await interaction.response.send_message(
                    "❌ Valor deve ser maior que 0",
                    ephemeral=True
                )
                return
            
            if amount > self.balance:
                await interaction.response.send_message(
                    f"❌ Você tem apenas R$ {self.balance:.2f} disponível",
                    ephemeral=True
                )
                return
            
            # Encontrar a instância do PaymentCog
            payment_cog = None
            for cog in interaction.client.cogs.values():
                if cog.__class__.__name__ == 'PaymentCog':
                    payment_cog = cog
                    break
            
            if not payment_cog:
                await interaction.response.send_message("❌ Erro ao processar saque.", ephemeral=True)
                return
            
            # Chamar a função withdraw com o amount
            await payment_cog.withdraw(interaction, amount=amount)
        
        except ValueError:
            await interaction.response.send_message(
                "❌ Valor inválido. Use números (ex: 10.50 ou 10,50)",
                ephemeral=True
            )
        except Exception as e:
            print(f"[MODAL] Erro em ModalEscolherValorSaque: {e}")
            await interaction.response.send_message(f"❌ Erro ao processar: {str(e)}", ephemeral=True)
