from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Rota principal para testes rápidos no navegador
@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "Servidor Python online! Aguardando dados do produto."})

# Rota EXATA que o seu front-end está chamando (/api/analisar)
@app.route('/api/analisar', methods=['POST'])
def analisar_produto():
    data = request.get_json() or {}
    product_name = data.get('product_name')
    market = data.get('market', 'Europa')
    language = data.get('language', 'Português')

    if not product_name:
        return jsonify({"error": "Faltando o nome do produto (product_name)."}), 400

    openrouter_key = os.environ.get("OPENROUTER_API_KEY")
    if not openrouter_key:
        return jsonify({"error": "Chave OPENROUTER_API_KEY nao configurada nas variaveis de ambiente da Vercel."}), 500

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
        # Llama 3 8B gratuito: Altamente estável e veloz para evitar timeouts de 10s da Vercel
        "model": "meta-llama/llama-3-8b-instruct:free",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=8)
        
        # Se o OpenRouter retornar qualquer status de erro (401, 403, 429), captura o texto puro
        if response.status_code != 200:
            return jsonify({
                "error": f"O OpenRouter retornou status HTTP {response.status_code}",
                "detalhes": response.text[:250]
            }), 500

        res_data = response.json()

        if "error" in res_data:
            return jsonify({"error": f"Erro interno do OpenRouter: {res_data['error'].get('message')}"}), 400

        # Validação da estrutura exata do dicionário do OpenRouter/OpenAI
        if "choices" in res_data and len(res_data["choices"]) > 0:
            texto_ia = res_data['choices'][0]['message']['content']
            return jsonify({"resultado": texto_ia})
        else:
            return jsonify({
                "error": "Estrutura de resposta inesperada do OpenRouter.",
                "resposta_crua": res_data
            }), 500

    except requests.exceptions.Timeout:
        return jsonify({"error": "A requisicao ao OpenRouter demorou demais (Timeout)."}), 504
    except Exception as e:
        return jsonify({"error": f"Erro interno no processamento do servidor Python: {str(e)}"}), 500
