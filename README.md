# Asistente-Legal-RAG-con-Gemini-y-Flask-para-Normativa-de-Construcción

🤖 Asistente Legal de Construcción 🏢
Este proyecto implementa un sistema de Generación Aumentada por Recuperación (RAG) que utiliza el modelo Gemini 2.5 Flash para responder preguntas específicas sobre la normativa legal colombiana vigente en materia de construcción y vivienda, complementando la información con la búsqueda en tiempo real (web grounding).

✨ Características Principales
Generación Aumentada por Recuperación (RAG): Utiliza un archivo fine.json especializado en leyes de construcción para garantizar respuestas precisas y autorizadas.

Búsqueda en Tiempo Real (Web Grounding): Emplea la herramienta de búsqueda de Google (Gemini Search Grounding) para responder preguntas generales o consultas sobre información no contenida en la base de datos local.

Advertencia de Disclaimer: Incluye una advertencia clara ([NOTA: Información de internet]) en las respuestas que no provienen de la base de datos legal interna.

Tecnologías: Desarrollado con Python, Flask (Backend) y JavaScript/HTML/CSS (Frontend).

CORS Habilitado: Permite la comunicación segura entre el frontend (servido en un puerto diferente, ej. Live Server 5500) y el backend (servido en el puerto 5000).

🛠️ Requisitos e Instalación
Requisitos Previos
Antes de comenzar, asegúrate de tener instalado:

Python 3.x

Una Clave API de Google Gemini (obtenida en Google AI Studio).

Instalación del Entorno

Bash

python -m venv venv
source venv/bin/activate  # En Linux/macOS
.\venv\Scripts\activate   # En Windows
Instalar las dependencias de Python:

Bash

pip install Flask google-generativeai google-genai
🚀 Configuración y Ejecución
1. Configuración de la API Key
Abre el archivo app.py y reemplaza el marcador de posición TU_API_KEY_AQUI con tu clave API real:

Python

# EN app.py
os.environ["GOOGLE_API_KEY"] = "TU_API_KEY_AQUI" 

2. Base de Conocimiento (RAG)
Asegúrate de que el archivo fine.json esté en el mismo directorio que app.py. Este archivo contiene la información legal especializada que alimenta el RAG.

3. Ejecución del Backend (Servidor Flask)
Inicia el servidor Python en una terminal:

Bash

python app.py
Deberías ver el mensaje: Servidor MDM corriendo en puerto 5000...

4. Ejecución del Frontend (Página Web)
Abre el archivo index.html en tu navegador. Recomendamos usar la extensión Live Server de VS Code para servir la página en un puerto local (ej. http://127.0.0.1:5500).

El frontend se comunicará con el backend en el puerto 5000.

❓ Modo de Uso
Consulta RAG (Interna): Preguntas sobre normativa específica contenida en fine.json.

Ejemplo: "¿Qué modifica el Decreto 1166 de 2025 en relación con las licencias de construcción?"

Respuesta: Contenido especializado, SIN disclaimer.

Consulta Web (Grounding): Preguntas de conocimiento general o información actual.

Ejemplo: "¿Cuál es el precio actual del dólar en Colombia?"

Respuesta: Contenido de búsqueda en internet, CON el disclaimer: [NOTA: Información de internet].

📂 Estructura del Proyecto
.
├── app.py              # Backend: Lógica principal de Flask, RAG, Gemini API y CORS.
├── fine.json           # Base de conocimiento especializada para el RAG.
├── index.html          # Frontend: Estructura HTML de la interfaz del chat.
└── script.js           # Frontend: Lógica de conexión AJAX/fetch para enviar mensajes.
