import os
from dotenv import load_dotenv
import requests

load_dotenv()

CLIENT_ID = os.getenv("MISTICPAY_CLIENT_ID")
CLIENT_SECRET = os.getenv("MISTICPAY_CLIENT_SECRET")
API_URL = "https://api.misticpay.com/api"

print(f"Client ID: {CLIENT_ID}")
print(f"Client Secret: {CLIENT_SECRET}")
print(f"API URL: {API_URL}")

headers = {
    'ci': CLIENT_ID,
    'cs': CLIENT_SECRET,
    'Content-Type': 'application/json'
}

# Teste GET /balance
try:
    response = requests.get(f'{API_URL}/users/balance', headers=headers, timeout=10)
    print(f"\nGET /users/balance")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:300]}")
except Exception as e:
    print(f"Erro GET: {e}")

# Teste POST /transactions/create (criar transação)
import time
payload = {
    "amount": 10.50,
    "payerName": "Cliente Teste",
    "payerDocument": "12345678909",
    "transactionId": f"test_{int(time.time())}",
    "description": "Teste de pagamento Discord Bot"
}

try:
    response = requests.post(f'{API_URL}/transactions/create', headers=headers, json=payload, timeout=10)
    print(f"\nPOST /transactions/create")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:500]}")
except Exception as e:
    print(f"Erro POST: {e}")
