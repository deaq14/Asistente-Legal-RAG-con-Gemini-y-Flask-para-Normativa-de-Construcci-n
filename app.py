import os
import json
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS

# --- VERIFICACIÓN DE VERSIÓN ---
print(f"Versión de la librería google-generativeai: {genai.__version__}")

# --- CONFIGURACIÓN DE FLASK ---
app = Flask(__name__)
CORS(app)

# --- CONFIGURACIÓN DE GEMINI ---
os.environ["GOOGLE_API_KEY"] = "TU API KEY DE GOOGLE"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# NOTA IMPORTANTE: Google Search NO está disponible como herramienta en la SDK de Python
# Solo está disponible en Google AI Studio y en la API REST directamente
# Usamos el modelo sin herramientas adicionales
model = genai.GenerativeModel('gemini-2.5-flash')

# --- BASE DE CONOCIMIENTO RAG ---
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, 'fine.json')

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        KNOWLEDGE_BASE = json.load(f)
    print(f"Base de conocimiento cargada: {file_path}")
except Exception as e:
    print(f"Nota: No se cargó fine.json. Se usará conocimiento del modelo.")
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
        return "CONTEXTO NO ENCONTRADO EN LA BASE DE DATOS LEGAL."

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        mensaje_usuario = data.get('message', '')

        if not mensaje_usuario:
            return jsonify({'respuesta': 'Por favor escribe un mensaje.'}), 400

        # 1. Recuperamos contexto local (RAG)
        contexto_inyectado = retrieve_context(mensaje_usuario, KNOWLEDGE_BASE)
        
        # 2. Determinamos si la pregunta necesita información actualizada
        palabras_clave_tiempo = ['actual', 'hoy', 'ahora', 'reciente', 'último', 'últimos', 
                                  'este año', '2024', '2025', 'clima', 'precio', 'cotización']
        necesita_info_actual = any(palabra in mensaje_usuario.lower() for palabra in palabras_clave_tiempo)

        # 3. Preparamos el Prompt
        if contexto_inyectado != "CONTEXTO NO ENCONTRADO EN LA BASE DE DATOS LEGAL.":
            # Tenemos información en la base de datos
            prompt_ingenieria = f"""
Actúa como el asistente virtual experto de la empresa "MDM Consultores e Inmobiliarios".

CONTEXTO LEGAL INYECTADO (Esta es tu fuente principal):
{contexto_inyectado}

PREGUNTA DEL CLIENTE:
{mensaje_usuario}

INSTRUCCIONES:
- Responde basándote ÚNICAMENTE en el contexto legal proporcionado
- Si el contexto no contiene la información específica, dilo claramente
- Mantén un tono profesional y claro
"""
        else:
            # No hay información en la base de datos, usamos conocimiento del modelo
            if necesita_info_actual:
                advertencia = "⚠️ **Nota:** Mi información tiene fecha de corte en enero 2025. Para información actualizada, te recomiendo verificar fuentes oficiales.\n\n"
            else:
                advertencia = ""
                
            prompt_ingenieria = f"""
Actúa como el asistente virtual experto de la empresa "MDM Consultores e Inmobiliarios".

La pregunta del cliente NO se encuentra en nuestra base de datos legal.

PREGUNTA DEL CLIENTE:
{mensaje_usuario}

INSTRUCCIONES:
- Proporciona la mejor respuesta posible basada en tu conocimiento general
- Si es un tema legal colombiano, ofrece información general útil
- Si necesita información actualizada más allá de enero 2025, indícalo claramente
- Mantén un tono profesional y claro
"""

        # 4. Llamada al modelo
        response = model.generate_content(prompt_ingenieria)
        
        respuesta_final = response.text
        if necesita_info_actual and contexto_inyectado == "CONTEXTO NO ENCONTRADO EN LA BASE DE DATOS LEGAL.":
            respuesta_final = f"⚠️ **Nota:** Mi información tiene fecha de corte en enero 2025. Para datos actualizados, verifica fuentes oficiales.\n\n{respuesta_final}"
        
        return jsonify({'respuesta': respuesta_final})

    except Exception as e:
        print(f"Error detallado: {e}")
        return jsonify({'respuesta': f'Error del servidor: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok', 
        'model': 'gemini-2.0-flash-exp',
        'note': 'Google Search no disponible en SDK Python. Usar API REST si se requiere.'
    })

if __name__ == '__main__':
    print("=" * 60)
    print("Servidor MDM corriendo en puerto 5000...")
    print("IMPORTANTE: Google Search NO está disponible en la SDK de Python")
    print("Solo funciona vía API REST o Google AI Studio")
    print("=" * 60)
    app.run(debug=True, port=5000)