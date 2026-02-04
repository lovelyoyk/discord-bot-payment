from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from payment_handler import MisticPayHandler
from database import add_balance, get_payment_channel, add_transaction_history, safe_add_balance
import hmac
import hashlib
import discord
from discord.ext import commands
import asyncio
import threading
from wallet_components import criar_embed_notificacao_pagamento
from utils.webhook_validator import webhook_validator
from utils.logger import setup_logger

load_dotenv()

app = Flask(__name__)
CORS(app)
payment_handler = MisticPayHandler()
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")

# Logger
logger = None  # Será setado pelo main.py

# Emojis para notificações
EMOJI_SUCESSO = os.getenv("EMOJI_SUCESSO", "✅")
EMOJI_CLIENTE = os.getenv("EMOJI_CLIENTE", "👥")
EMOJI_VENDEDOR = os.getenv("EMOJI_VENDEDOR", "👤")
EMOJI_VALOR = os.getenv("EMOJI_VALOR", "💰")
EMOJI_PAGAMENTO = os.getenv("EMOJI_PAGAMENTO", "💳")

# Referência global para o bot (será setada pelo main.py)
bot_instance = None

@app.route("/webhook", methods=["GET"])
def webhook_test():
    """Rota de teste para verificar se o webhook está acessível."""
    return jsonify({
        "status": "online",
        "message": "Webhook endpoint está funcionando! Use POST para enviar webhooks.",
        "timestamp": __import__('datetime').datetime.now().isoformat()
    }), 200

@app.route("/webhook", methods=["POST"])
def misticpay_webhook():
    """Webhook para receber notificações de pagamento MisticPay."""
    
    try:
        # Obter dados
        data = request.get_json()
        payload = request.get_data().decode('utf-8')
        signature = request.headers.get("X-Signature", "")
        
        # Log DETALHADO do webhook recebido
        event_type = data.get('event', 'unknown') if data else 'unknown'
        if logger:
            logger.info(f"🔔 [WEBHOOK] Evento recebido: {event_type}")
            logger.info(f"📨 [WEBHOOK] Payload completo: {data}")
            logger.info(f"📋 [WEBHOOK] Data field: {data.get('data', {}) if data else 'Nenhum'}")
        
        print(f"\n{'='*80}")
        print(f"[Webhook Server] ⏰ {__import__('datetime').datetime.now().isoformat()}")
        print(f"[Webhook Server] 📨 Payload completo:")
        print(f"{data}")
        print(f"[Webhook Server] 🔍 Event type: {event_type}")
        print(f"[Webhook Server] 📋 Data field: {data.get('data', {}) if data else 'Nenhum'}")
        print(f"{'='*80}\n")
        
        # Validar webhook com sistema de segurança (DESABILITADO TEMPORARIAMENTE)
        # if not webhook_validator.validate_webhook(payload, signature, data):
        #     if logger:
        #         logger.warning("Webhook rejeitado: validação falhou")
        #     return jsonify({"status": "invalid"}), 401
        
        # Processar webhook
        result = payment_handler.verify_webhook(data)
        
        if result and result["status"] == "completed":
            receiver_id = result["receiver_id"]
            amount = result["amount"]
            payment_id = result["payment_id"]
            
            # Extrair ref do MisticPay
            ref = data.get("data", {}).get("id", payment_id)
            gross_amount = amount
            
            # Log da transação
            if logger:
                logger.info(f"Pagamento confirmado: UserID {receiver_id} | R$ {amount:.2f} | ID {payment_id}")
            
            # Adiciona saldo ao vendedor COM SEGURANÇA (evita race conditions)
            safe_add_balance(
                receiver_id, 
                amount, 
                f"Pagamento recebido - MisticPay {payment_id}"
            )
            
            # Adicionar ao histórico detalhado
            add_transaction_history(
                receiver_id,
                "payment",
                amount,
                f"Pagamento recebido",
                gross_amount=gross_amount,
                misticpay_ref=ref
            )
            
            # Notificar no Discord via bot
            if bot_instance:
                asyncio.run_coroutine_threadsafe(
                    notificar_pagamento(receiver_id, amount, payment_id, ref, gross_amount),
                    bot_instance.loop
                )
            
            return jsonify({
                "status": "success",
                "receiver_id": receiver_id,
                "amount": amount,
                "payment_id": payment_id,
                "ref": ref
            }), 200
        
        return jsonify({"status": "no_action"}), 200
        
    except Exception as e:
        if logger:
            logger.error(f"Erro no webhook: {e}")
        print(f"Erro no webhook: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400

async def notificar_pagamento(receiver_id: int, amount: float, payment_id: str, ref: str, gross_amount: float):
    """Notifica o pagamento no canal e envia DM ao usuário"""
    try:
        # Buscar canal onde foi criada a cobrança
        channel_id = get_payment_channel(payment_id)
        
        # Enviar mensagem no canal se houver
        if channel_id and bot_instance:
            try:
                channel = bot_instance.get_channel(channel_id)
                if channel:
                    user = await bot_instance.fetch_user(receiver_id)
                    
                    # Criar embed com nova notificação
                    embed = criar_embed_notificacao_pagamento(
                        cliente="Cliente",  # TODO: Buscar nome do cliente
                        vendedor=user.name,
                        valor=amount,
                        valor_bruto=gross_amount,
                        ref=ref,
                        emoji_sucesso=EMOJI_SUCESSO
                    )
                    
                    await channel.send(embed=embed)
            except Exception as e:
                print(f"Erro ao enviar notificação no canal: {e}")
        
        # Também enviar DM para o usuário
        user = await bot_instance.fetch_user(receiver_id)
        
        embed = discord.Embed(
            title="✅ Pagamento Recebido",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="💰 Valor",
            value=f"R$ {amount:.2f}",
            inline=True
        )
        
        embed.add_field(
            name="📌 ID",
            value=f"`{payment_id}`",
            inline=True
        )
        
        embed.add_field(
            name="🔗 Referência",
            value=f"`{ref}`",
            inline=False
        )
        
        await user.send(embed=embed)
    
    except Exception as e:
        print(f"Erro ao notificar pagamento: {e}")

@app.route("/health", methods=["GET"])
def health():
    """Verifica se o webhook está rodando."""
    return jsonify({"status": "online", "service": "MisticPay Webhook"}), 200

def run_webhook():
    """Roda o servidor Flask em thread separada"""
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)

if __name__ == "__main__":
    run_webhook()


