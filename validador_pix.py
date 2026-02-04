import re
from typing import Tuple

class ValidadorPIX:
    """Validador para diferentes tipos de chave PIX"""
    
    @staticmethod
    def validar_cpf(cpf: str) -> Tuple[bool, str]:
        """Valida CPF: 000.000.000-00 ou 00000000000"""
        # Remove caracteres especiais
        cpf = re.sub(r'\D', '', cpf)
        
        if len(cpf) != 11:
            return False, "CPF deve ter 11 dígitos"
        
        if cpf == cpf[0] * 11:  # Todos iguais
            return False, "CPF inválido (todos dígitos iguais)"
        
        # Validação de dígito verificador (simplificada)
        try:
            int(cpf)
            return True, cpf
        except:
            return False, "CPF contém caracteres inválidos"
    
    @staticmethod
    def validar_email(email: str) -> Tuple[bool, str]:
        """Valida email"""
        padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(padrao, email):
            return False, "Email inválido"
        
        if len(email) > 254:
            return False, "Email muito longo"
        
        return True, email.lower()
    
    @staticmethod
    def validar_telefone(telefone: str) -> Tuple[bool, str]:
        """Valida telefone: qualquer DDD + 9 dígitos para celular ou 8 para fixo
        
        Formatos aceitos:
        - (11) 9 1234-5678
        - 11 91234-5678
        - 11991234567
        - (11) 3123-4567 (fixo)
        """
        # Remove caracteres especiais
        telefone_limpo = re.sub(r'\D', '', telefone)
        
        # Deve ter 10 (fixo) ou 11 (celular) dígitos
        if len(telefone_limpo) == 10:
            # Fixo: 2 dígitos DDD + 8 dígitos
            if not re.match(r'^\d{2}[2-5]\d{7}$', telefone_limpo):
                return False, "Telefone fixo inválido (formato: xx 2xxxx-xxxx até xx 5xxxx-xxxx)"
        elif len(telefone_limpo) == 11:
            # Celular: 2 dígitos DDD + 9 dígitos (começando com 9)
            if not re.match(r'^\d{2}9\d{8}$', telefone_limpo):
                return False, "Celular inválido (formato: xx 9xxxx-xxxx)"
        else:
            return False, "Telefone deve ter 10 ou 11 dígitos"
        
        # Validação básica do DDD (11-99)
        ddd = int(telefone_limpo[:2])
        if ddd < 11 or ddd > 99:
            return False, "DDD inválido"
        
        return True, telefone_limpo
    
    @staticmethod
    def validar_chave_aleatoria(chave: str) -> Tuple[bool, str]:
        """Valida chave aleatória (UUID format)"""
        # Remove hífen se existir
        chave_limpa = chave.replace('-', '')
        
        # UUID tem 32 caracteres hexadecimais
        if len(chave_limpa) != 32:
            return False, "Chave aleatória deve ter 32 caracteres hexadecimais"
        
        if not re.match(r'^[0-9a-f]{32}$', chave_limpa, re.IGNORECASE):
            return False, "Chave aleatória deve conter apenas números e letras"
        
        return True, chave_limpa
    
    @staticmethod
    def validar_pix(chave: str) -> Tuple[bool, str, str]:
        """Detecta tipo e valida a chave PIX
        
        Retorna: (válido, mensagem, tipo_chave)
        """
        chave = chave.strip()
        
        # Tenta CPF
        if re.match(r'^\d{3}\.\d{3}\.\d{3}-\d{2}$|^\d{11}$', chave):
            valido, msg = ValidadorPIX.validar_cpf(chave)
            if valido:
                return True, msg, "CPF"
            return False, msg, "CPF"
        
        # Tenta Email
        if '@' in chave:
            valido, msg = ValidadorPIX.validar_email(chave)
            if valido:
                return True, msg, "Email"
            return False, msg, "Email"
        
        # Tenta Telefone
        if any(c.isdigit() for c in chave):
            # Pode ser telefone se não tem @ e formato parece telefone
            if len(re.sub(r'\D', '', chave)) in [10, 11]:
                valido, msg = ValidadorPIX.validar_telefone(chave)
                if valido:
                    return True, msg, "Telefone"
        
        # Tenta Chave Aleatória
        if len(re.sub(r'-', '', chave)) == 32:
            valido, msg = ValidadorPIX.validar_chave_aleatoria(chave)
            if valido:
                return True, msg, "Chave Aleatória"
            return False, msg, "Chave Aleatória"
        
        return False, "Tipo de chave PIX não reconhecido. Use: CPF, Email, Telefone ou Chave Aleatória", "Desconhecido"
