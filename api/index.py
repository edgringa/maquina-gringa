from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

@app.route('/', defaults={'path': ''}, methods=['POST', 'GET'])
@app.route('/<path:path>', methods=['POST', 'GET'])
def catch_all(path):
    if request.method == 'GET':
        return jsonify({"status": "Servidor Python online! Aguardando dados do produto."})

    data = request.get_json() or {}
    product_name = data.get('product_name')
    market = data.get('market')
    language = data.get('language')

    if not product_name:
        return jsonify({"error": "Faltando o nome do produto."}), 400

    openrouter_key = os.environ.get("OPENROUTER_API_KEY")
    if not openrouter_key:
        return jsonify({"error": "Chave OPENROUTER_API_KEY nao configurada na Vercel."}), 500

    prompt = f"""Você é um gestor de tráfego pago especialista em afiliados na Europa (Smartadv). Analise o produto "{product_name}" para o mercado "{market}" no idioma "{language}". Gere: 1. ANÁLISE DE DORES OCULTAS 2. QUEBRA DE OBJEÇÕES DE MEIO DE FUNIL 3. ANÚNCIOS RSA: 3 títulos (máx 30 carac.) e 2 descrições (máx 90 carac.) em "{language}". 4. FILTRO DE COMPLIANCE (ANTI-BLOQUEIO) Responda em Português, mas os anúncios devem estar em "{language}"."""

    url = "https://openrouter.ai"
    
    headers = {
        "Authorization": f"Bearer {openrouter_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "meta-llama/llama-3.3-70b-instruct:free",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        res_data = response.json()

        if "error" in res_data:
            return jsonify({"error": f"Erro do OpenRouter: {res_data['error'].get('message')}"}), 400

        # Correção crucial: Adicionado o índice [0] para ler a primeira opção da lista
        texto_ia = res_data['choices'][0]['message']['content']
        return jsonify({"resultado": texto_ia})

    except Exception as e:
        return jsonify({"error": f"Erro na IA: {str(e)}"}), 500
