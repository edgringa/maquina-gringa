from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Aceita tanto a rota com o prefixo quanto a rota raiz da função
@app.route('/api/analisar', methods=['POST', 'GET'])
@app.route('/', methods=['POST', 'GET'])
def analisar_produto():
    # Se for uma requisição GET (teste no navegador), avisa que está online
    if request.method == 'GET':
        return jsonify({"status": "Servidor Python online! Envie os dados via POST."})

    # Pega os dados enviados pelo front-end
    data = request.get_json() or {}
    
    # Busca por qualquer variação de nome que o seu front-end possa ter enviado
    product_name = data.get('product_name') or data.get('nome') or data.get('produto')
    market = data.get('market') or data.get('mercado') or 'Europa'
    language = data.get('language') or data.get('idioma') or 'Português'

    # Se mesmo assim não achar nada, mostra o que o front-end enviou de verdade para ajudar no diagnóstico
    if not product_name:
        return jsonify({
            "error": "Faltando o nome do produto.",
            "dados_recebidos_pelo_front": data
        }), 400

    openrouter_key = os.environ.get("OPENROUTER_API_KEY")
    if not openrouter_key:
        return jsonify({"error": "Chave OPENROUTER_API_KEY nao configurada na Vercel."}), 500

    prompt = f"""Você é um gestor de tráfego pago especialista em afiliados na Europa (Smartadv) focado em campanhas de Meio de Funil. 
Analise o produto "{product_name}" para o mercado "{market}" no idioma "{language}". 
Gere: 
1. ANÁLISE DE DORES OCULTAS 
2. QUEBRA DE OBJEÇÕES DE MEIO DE FUNIL 
3. ANÚNCIOS RSA: 3 títulos e 2 descrições em "{language}". 
4. FILTRO DE COMPLIANCE. 
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
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        if response.status_code != 200:
            return jsonify({
                "error": f"Erro do OpenRouter (Status {response.status_code})",
                "detalhes": response.text[:200]
            }), 500

        res_data = response.json()
        texto_ia = res_data['choices'][0]['message']['content']
        return jsonify({"resultado": texto_ia})

    except Exception as e:
        return jsonify({"error": f"Erro interno no servidor: {str(e)}"}), 500
