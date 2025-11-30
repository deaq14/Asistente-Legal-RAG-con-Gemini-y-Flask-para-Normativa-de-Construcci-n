import os
import json
from google import genai
from google.genai.types import (
    GenerateContentConfig,
    GoogleSearch,
    HttpOptions,
    Tool,
)
from flask import Flask, request, jsonify
from flask_cors import CORS

# --- CONFIGURACIÓN DE FLASK ---
app = Flask(__name__)
CORS(app)

# --- CONFIGURACIÓN DE GEMINI ---
os.environ["GOOGLE_API_KEY"] = "AIzaSyAmSCctoYYkrER6LVjHn9aHCsetkxR4vu8"

# Cliente con la nueva SDK
client = genai.Client(
    api_key=os.environ["GOOGLE_API_KEY"],
    http_options=HttpOptions(api_version="v1alpha")
)

# --- BASE DE CONOCIMIENTO RAG ---
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, 'fine.json')

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        KNOWLEDGE_BASE = json.load(f)
    print(f"Base de conocimiento cargada: {file_path}")
except Exception as e:
    print(f"Nota: No se cargó fine.json. Se usará búsqueda web.")
    KNOWLEDGE_BASE = []

def retrieve_context(query, knowledge_base):
    query_lower = query.lower()
    relevant_contexts = []
    
    for item in knowledge_base:
        context = item.get("context", "").lower()
        question = item.get("question", "").lower()
        stop_words = ["la", "el", "de", "un", "una", "qué", "en", "o"]
        query_words = [word for word in query_lower.split() if word not in stop_words]
        
        if any(word in context or word in question for word in query_words):
            relevant_contexts.append(item.get("context"))

    if relevant_contexts:
        return "\n---\n".join(relevant_contexts[:5])
    else:
        return None

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        mensaje_usuario = data.get('message', '')

        if not mensaje_usuario:
            return jsonify({'respuesta': 'Por favor escribe un mensaje.'}), 400

        # 1. Recuperamos contexto local (RAG)
        contexto_inyectado = retrieve_context(mensaje_usuario, KNOWLEDGE_BASE)

        # 2. Preparamos el Prompt
        if contexto_inyectado:
            # Tenemos información en nuestra base de datos
            prompt = f"""
Actúa como el asistente virtual experto de la empresa "MDM Consultores e Inmobiliarios".

CONTEXTO LEGAL INTERNO (Tu fuente principal):
{contexto_inyectado}

PREGUNTA DEL CLIENTE:
{mensaje_usuario}

INSTRUCCIONES:
- Responde basándote principalmente en el contexto legal interno
- Si el contexto no es suficiente, puedes complementar con búsqueda web
- Si usas información de internet, inicia con: "**[Información complementaria de internet]**"
- Mantén un tono profesional y claro
"""
            usar_busqueda = True  # Permitimos búsqueda como complemento
        else:
            # No hay información en la base, usamos búsqueda web directamente
            prompt = f"""
Actúa como el asistente virtual experto de la empresa "MDM Consultores e Inmobiliarios".

PREGUNTA DEL CLIENTE:
{mensaje_usuario}

INSTRUCCIONES:
- Busca información actualizada y relevante
- Inicia tu respuesta con: "**[Información de internet]**"
- Proporciona información precisa y verificable
- Mantén un tono profesional y claro
"""
            usar_busqueda = True

        # 3. Configuración de herramientas
        config = GenerateContentConfig(
            tools=[Tool(google_search=GoogleSearch())]
        ) if usar_busqueda else None

        # 4. Llamada al modelo con Google Search
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=config
        )
        
        return jsonify({'respuesta': response.text})

    except Exception as e:
        print(f"Error detallado: {e}")
        return jsonify({'respuesta': f'Error del servidor: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok', 
        'model': 'gemini-2.5-flash',
        'google_search': 'enabled'
    })

if __name__ == '__main__':
    print("=" * 60)
    print("Servidor MDM corriendo en puerto 5000...")
    print("✓ Google Search HABILITADO")
    print("✓ Base de conocimiento RAG activa")
    print("=" * 60)
    app.run(debug=True, port=5000)