// Lógica para Abrir/Cerrar el Chat
function toggleChat() {
    const chatWindow = document.getElementById('chatWindow');
    chatWindow.classList.toggle('open');
    if(chatWindow.classList.contains('open')){
        document.getElementById('userInput').focus();
    }
}

// Manejar tecla Enter
function handleKeyPress(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

// Lógica de Envío de Mensajes (Conexión al Backend Python/Gemini)
function sendMessage() {
    const inputField = document.getElementById('userInput');
    const messageText = inputField.value.trim();
    const chatMessages = document.getElementById('chatMessages');

    if (messageText === "") return;

    // 1. Mostrar mensaje del usuario
    addMessage(messageText, 'user');
    inputField.value = ''; 

    // 2. Mostrar indicador de "Escribiendo..."
    const loadingDiv = document.createElement('div');
    loadingDiv.classList.add('message', 'bot');
    loadingDiv.innerText = "Consultando normativa...";
    loadingDiv.id = "loadingMessage";
    chatMessages.appendChild(loadingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // 3. Llamada al Backend (RAG)
    // Usamos el puerto 5000 del servidor Python
    fetch('http://127.0.0.1:5000/chat', { 
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: messageText })
    })
    .then(response => {
        // Manejo explícito de errores HTTP/JSON
        if (!response.ok) {
            // Esto captura errores 404, 500, etc., y los reporta en el chat.
            throw new Error(`Error de Servidor: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        // Eliminar mensaje de carga
        const loadingMsg = document.getElementById('loadingMessage');
        if(loadingMsg) loadingMsg.remove();

        // Mostrar respuesta de Gemini
        addMessage(data.respuesta, 'bot'); 
    })
    .catch(error => {
        console.error('Error de Conexión o Servidor:', error);
        const loadingMsg = document.getElementById('loadingMessage');
        if(loadingMsg) loadingMsg.remove();
        // Mostrar un error legible al usuario
        addMessage(`⚠️ Error en la conexión. Revisa la consola o tu API Key. Detalles: ${error.message}`, 'bot');
    });
}

// Función auxiliar para crear HTML de mensajes
function addMessage(text, sender) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', sender);
    messageDiv.innerText = text;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}