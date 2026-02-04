"""
Configurações de Proprietários e Permissões

Este arquivo contém as configurações hardcoded de proprietários (donos) do bot.
Apenas os usuários nesta lista podem executar comandos administrativos.
"""

import os

# Lista de IDs dos proprietários do bot (HARDCODED)
# Adicione aqui os IDs Discord dos usuários que devem ter acesso a comandos de owner
OWNER_IDS = [
    429035977667772418,  # ID do Dono Principal
    # Adicione mais IDs aqui:
    # 123456789,
    # 987654321,
]

def is_owner(user_id: int) -> bool:
    """Verifica se um usuário é proprietário do bot."""
    return user_id in OWNER_IDS

def get_owner_ids() -> list:
    """Retorna lista de owner IDs."""
    return OWNER_IDS.copy()
