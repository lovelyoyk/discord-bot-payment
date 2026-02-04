"""
Sistema de Logging Completo
Registra todos os eventos importantes do bot em arquivos e console
"""
import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

def setup_logger(name: str = "bot"):
    """Configura o sistema de logging do bot"""
    
    # Criar diretório de logs se não existir
    log_dir = "./logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configurar logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Formato das mensagens
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para arquivo (rotativo - máx 10MB, mantém 5 backups)
    file_handler = RotatingFileHandler(
        f"{log_dir}/bot.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    
    # Handler para erros (arquivo separado)
    error_handler = RotatingFileHandler(
        f"{log_dir}/errors.log",
        maxBytes=10*1024*1024,
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    
    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Adicionar handlers
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)
    logger.addHandler(console_handler)
    
    return logger

def log_payment(logger, user_id: int, amount: float, payment_id: str, status: str):
    """Registra transação de pagamento"""
    logger.info(f"PAYMENT | UserID: {user_id} | Amount: R$ {amount:.2f} | ID: {payment_id} | Status: {status}")

def log_withdrawal(logger, user_id: int, amount: float, payout_id: str, status: str):
    """Registra saque"""
    logger.info(f"WITHDRAW | UserID: {user_id} | Amount: R$ {amount:.2f} | ID: {payout_id} | Status: {status}")

def log_refund(logger, user_id: int, amount: float, refund_id: int, status: str):
    """Registra reembolso"""
    logger.info(f"REFUND | UserID: {user_id} | Amount: R$ {amount:.2f} | ID: {refund_id} | Status: {status}")

def log_error(logger, error_type: str, error_msg: str, user_id: int = None):
    """Registra erro"""
    if user_id:
        logger.error(f"ERROR | Type: {error_type} | UserID: {user_id} | Message: {error_msg}")
    else:
        logger.error(f"ERROR | Type: {error_type} | Message: {error_msg}")

def log_command(logger, command: str, user_id: int, guild_id: int = None):
    """Registra uso de comando"""
    if guild_id:
        logger.info(f"COMMAND | {command} | UserID: {user_id} | GuildID: {guild_id}")
    else:
        logger.info(f"COMMAND | {command} | UserID: {user_id}")

def log_webhook(logger, event_type: str, data: dict):
    """Registra evento de webhook"""
    logger.info(f"WEBHOOK | Type: {event_type} | Data: {data}")
