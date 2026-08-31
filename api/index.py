from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Ajustado para funcionar perfeitamente dentro da pasta api/
@app.route('/api/analisar', methods=['POST'])
@app.route('/', methods=['POST'])
def analisar_produto():
    data = request.get_json() or {}
    product_name = data.get('product_name')
    market = data.get('market', 'Europa')
    language = data.get('language', 'Português')

    if not product_name:
        return jsonify({"error": "Faltando o nome do produto (product_name)."}), 400

    openrouter_key = os.environ.get("OPENROUTER_API_KEY")
    if not openrouter_key:
        return jsonify({"error": "Chave OPENROUTER_API_KEY nao configurada na Vercel."}), 500

    prompt = f"""Você é um gestor de tráfego pago especialista em afiliados na Europa (Smartadv) focado em campanhas de Meio de Funil. 
Analise o produto "{product_name}" para o mercado "{market}" no idioma "{language}". 
Gere: 1. ANÁLISE DE DORES OCULTAS 2. QUEBRA DE OBJEÇÕES DE MEIO DE FUNIL 3. ANÚNCIOS RSA: 3 títulos e 2 descrições em "{language}". 4. FILTRO DE COMPLIANCE. 
Responda em Português, mas os anúncios devem estar em "{language}"."""

    url = "https://openrouter.ai"
    
    headers = {
        "Authorization": f"Bearer {openrouter_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "meta-llama/llama-3-8b-instruct:free",
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=8)
        
        if response.status_code != 200:
            return jsonify({
                "error": f"Erro do OpenRouter (Status {response.status_code})",
                "detalhes": response.text[:200]
            }), 500

        res_data = response.json()
        texto_ia = res_data['choices']['message']['content']
        return jsonify({"resultado": texto_ia})

    except Exception as e:
        return jsonify({"error": f"Erro interno no servidor: {str(e)}"}), 500
