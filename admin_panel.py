from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime, timedelta
from collections import defaultdict

app = Flask(__name__, template_folder='templates')
CORS(app)

DB_PATH = os.getenv("DATABASE_PATH", "./data/bot.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def index():
    db = get_db()
    
    # Filtros
    status_filter = request.args.get('status', 'all')
    search = request.args.get('search', '')
    
    # Query de pagamentos com filtro
    query = "SELECT * FROM payments WHERE 1=1"
    params = []
    
    if status_filter != 'all':
        query += " AND status = ?"
        params.append(status_filter)
    
    if search:
        query += " AND (CAST(receiver_id AS TEXT) LIKE ? OR CAST(payer_id AS TEXT) LIKE ? OR payment_id LIKE ? OR misticpay_id LIKE ?)"
        search_param = f"%{search}%"
        params.extend([search_param, search_param, search_param, search_param])
    
    query += " ORDER BY created_at DESC LIMIT 50"
    
    pagamentos = db.execute(query, params).fetchall()
    reembolsos = db.execute("SELECT * FROM refunds ORDER BY created_at DESC LIMIT 20").fetchall()
    usuarios = db.execute("SELECT * FROM users ORDER BY balance DESC LIMIT 50").fetchall()
    
    # Estatísticas
    total_pagamentos = db.execute("SELECT COUNT(*) as count FROM payments WHERE status = 'completed'").fetchone()['count']
    valor_total = db.execute("SELECT SUM(amount) as total FROM payments WHERE status = 'completed'").fetchone()['total'] or 0
    total_usuarios = db.execute("SELECT COUNT(*) as count FROM users").fetchone()['count']
    total_reembolsos = db.execute("SELECT COUNT(*) as count FROM refunds").fetchone()['count']
    valor_reembolsos = db.execute("SELECT SUM(amount) as total FROM refunds").fetchone()['total'] or 0
    
    # Pagamentos pendentes
    pagamentos_pendentes = db.execute("SELECT COUNT(*) as count FROM payments WHERE status = 'pending'").fetchone()['count']
    
    # Ultimas transações para dashboard
    ultimas_transacoes = db.execute("SELECT * FROM payments ORDER BY created_at DESC LIMIT 10").fetchall()
    
    db.close()
    
    return render_template("admin_index.html", 
                         pagamentos=pagamentos, 
                         reembolsos=reembolsos,
                         usuarios=usuarios,
                         total_pagamentos=total_pagamentos,
                         valor_total=valor_total,
                         total_usuarios=total_usuarios,
                         total_reembolsos=total_reembolsos,
                         valor_reembolsos=valor_reembolsos,
                         pagamentos_pendentes=pagamentos_pendentes,
                         ultimas_transacoes=ultimas_transacoes,
                         status_filter=status_filter,
                         search=search)

@app.route('/api/stats')
def api_stats():
    db = get_db()
    
    # Estatísticas dos últimos 7 dias
    stats = []
    for i in range(7):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        count = db.execute("SELECT COUNT(*) as count FROM payments WHERE DATE(created_at) = ? AND status = 'completed'", (date,)).fetchone()['count']
        valor = db.execute("SELECT SUM(amount) as total FROM payments WHERE DATE(created_at) = ? AND status = 'completed'", (date,)).fetchone()['total'] or 0
        stats.append({'date': date, 'count': count, 'valor': float(valor)})
    
    db.close()
    return jsonify(stats[::-1])

@app.route('/api/payment/<payment_id>')
def api_payment(payment_id):
    db = get_db()
    payment = db.execute("SELECT * FROM payments WHERE payment_id = ?", (payment_id,)).fetchone()
    db.close()
    
    if payment:
        return jsonify(dict(payment))
    return jsonify({'error': 'Pagamento não encontrado'}), 404

@app.route('/health')
def health():
    return {"status": "online", "service": "MisticPay Webhook"}

@app.route('/api/reembolsos')
def api_reembolsos():
    db = get_db()
    
    # Filtros
    status_filter = request.args.get('status', 'all')
    
    # Query de reembolsos
    query = "SELECT id, user_id, amount, reason, status, created_at, approved_by, approved_at FROM refunds WHERE 1=1"
    params = []
    
    if status_filter != 'all':
        query += " AND status = ?"
        params.append(status_filter)
    
    query += " ORDER BY created_at DESC"
    
    reembolsos = db.execute(query, params).fetchall()
    db.close()
    
    return jsonify([dict(r) for r in reembolsos])

@app.route('/reembolsos')
def reembolsos_page():
    db = get_db()
    
    # Filtro de status
    status_filter = request.args.get('status', 'all')
    
    # Query de reembolsos
    query = "SELECT * FROM refunds WHERE 1=1"
    params = []
    
    if status_filter != 'all':
        query += " AND status = ?"
        params.append(status_filter)
    
    query += " ORDER BY created_at DESC"
    
    reembolsos = db.execute(query, params).fetchall()
    
    # Contadores
    total_reembolsos = db.execute("SELECT COUNT(*) as count FROM refunds").fetchone()['count']
    reembolsos_pendentes = db.execute("SELECT COUNT(*) as count FROM refunds WHERE status IN ('pending','pendente')").fetchone()['count']
    reembolsos_aprovados = db.execute("SELECT COUNT(*) as count FROM refunds WHERE status = 'aprovado'").fetchone()['count']
    reembolsos_rejeitados = db.execute("SELECT COUNT(*) as count FROM refunds WHERE status = 'rejeitado'").fetchone()['count']
    
    valor_total = db.execute("SELECT SUM(amount) as total FROM refunds").fetchone()['total'] or 0
    valor_aprovado = db.execute("SELECT SUM(amount) as total FROM refunds WHERE status = 'aprovado'").fetchone()['total'] or 0
    
    db.close()
    
    return render_template("reembolsos.html", 
                         reembolsos=reembolsos,
                         total_reembolsos=total_reembolsos,
                         reembolsos_pendentes=reembolsos_pendentes,
                         reembolsos_aprovados=reembolsos_aprovados,
                         reembolsos_rejeitados=reembolsos_rejeitados,
                         valor_total=valor_total,
                         valor_aprovado=valor_aprovado,
                         status_filter=status_filter)

if __name__ == "__main__":
    app.run(debug=True, port=5000, host='0.0.0.0')
