from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

@app.route('/api/analisar', methods=['POST'])
def analisar():
    data = request.get_json()
    product_name = data.get('product_name')
    market = data.get('market')
    language = data.get('language')
    
    # Pega a chave de forma segura das configurações da Vercel
    gemini_key = os.environ.get("GEMINI_API_KEY")
    
    if not gemini_key:
        return jsonify({"error": "Chave da API não configurada na Vercel."}), 500

    # Prompt cirúrgico para o Gemini
    prompt = f"""Você é um gestor de tráfego pago especialista em afiliados na Europa (Smartadv).
Analise o produto "{product_name}" para o mercado "{market}" no idioma "{language}".
Gere:
1. ANÁLISE DE DORES OCULTAS
2. QUEBRA DE OBJEÇÕES DE MEIO DE FUNIL
3. ANÚNCIOS RSA: 3 títulos (máx 30 carac.) e 2 descrições (máx 90 carac.) em "{language}".
4. FILTRO DE COMPLIANCE (ANTI-BLOQUEIO)
Responda em Português, mas os anúncios devem estar em "{language}"."""

    url = f"https://googleapis.com{gemini_key}"
    
    try:
        response = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
        res_data = response.json()
        
        texto_ia = res_data['candidates'][0]['content']['parts'][0]['text']
        return jsonify({"resultado": texto_ia})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
