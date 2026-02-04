import discord
from typing import Optional
import datetime

# URLs de ícones personalizados para thumbnails
ICONS = {
    "success": "https://cdn-icons-png.flaticon.com/512/5610/5610944.png",
    "error": "https://cdn-icons-png.flaticon.com/512/753/753345.png",
    "warning": "https://cdn-icons-png.flaticon.com/512/5974/5974627.png",
    "money": "https://cdn-icons-png.flaticon.com/512/3135/3135706.png",
    "pending": "https://cdn-icons-png.flaticon.com/512/2972/2972531.png",
    "payment": "https://cdn-icons-png.flaticon.com/512/2830/2830284.png",
    "dashboard": "https://cdn-icons-png.flaticon.com/512/1055/1055687.png",
    "history": "https://cdn-icons-png.flaticon.com/512/3503/3503786.png",
}

def criar_barra_progresso(porcentagem: int, tamanho: int = 10) -> str:
    """Cria uma barra de progresso visual."""
    completo = int((porcentagem / 100) * tamanho)
    incompleto = tamanho - completo
    return f"▰" * completo + f"▱" * incompleto + f" {porcentagem}%"

def criar_separador(texto: str = "") -> str:
    """Cria um separador visual elegante."""
    if texto:
        return f"━━━━━ {texto} ━━━━━"
    return "━━━━━━━━━━━━━━━━"

def formatar_valor(valor: float) -> str:
    """Formata valor monetário com estilo."""
    return f"💵 R$ {valor:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")

def padronizar_embed(
    embed: discord.Embed,
    interaction: Optional[discord.Interaction] = None,
    user: Optional[discord.abc.User] = None,
    footer: Optional[str] = None,
    icone_tipo: Optional[str] = None,
) -> discord.Embed:
    """Aplica padrão visual aos embeds com recursos visuais aprimorados."""
    # Ajuste automático de cores por tipo (se título indicar)
    if embed.title:
        title = embed.title.strip()
        if title.startswith("✅"):
            embed.color = discord.Color.green()
            if not icone_tipo: icone_tipo = "success"
        elif title.startswith("❌"):
            embed.color = discord.Color.red()
            if not icone_tipo: icone_tipo = "error"
        elif title.startswith("⚠️"):
            embed.color = discord.Color.orange()
            if not icone_tipo: icone_tipo = "warning"
        elif title.startswith("⏳"):
            embed.color = discord.Color.orange()
            if not icone_tipo: icone_tipo = "pending"
        elif title.startswith("💳"):
            embed.color = discord.Color.gold()
            if not icone_tipo: icone_tipo = "payment"
        elif title.startswith("💰"):
            embed.color = discord.Color.green()
            if not icone_tipo: icone_tipo = "money"
        elif title.startswith("📊"):
            embed.color = discord.Color.blue()
            if not icone_tipo: icone_tipo = "dashboard"
        elif title.startswith("📜"):
            embed.color = discord.Color.purple()
            if not icone_tipo: icone_tipo = "history"

    # Thumbnail personalizada por tipo
    if icone_tipo and icone_tipo in ICONS:
        if not embed.thumbnail or not embed.thumbnail.url:
            embed.set_thumbnail(url=ICONS[icone_tipo])
    elif user:
        try:
            if not embed.thumbnail or not embed.thumbnail.url:
                embed.set_thumbnail(url=user.display_avatar.url)
        except Exception:
            pass

    if interaction and embed.timestamp is None:
        embed.timestamp = interaction.created_at

    if footer:
        embed.set_footer(text=footer)
    else:
        if not (embed.footer and embed.footer.text):
            embed.set_footer(text="LS Aluguel • Financeiro")

    if interaction and not (embed.author and embed.author.name):
        try:
            bot_user = interaction.client.user
            if bot_user:
                embed.set_author(name="LS Aluguel • Financeiro", icon_url=bot_user.display_avatar.url)
        except Exception:
            pass

    return embed
