const token = localStorage.getItem("access_token");

if (!token) {
    console.error("Token not found in localStorage");
    window.location.href = "/login";
}

// Проверка токена
fetch("/protected", {
    method: "GET",
    headers: {
        Authorization: `Bearer ${token}`
    }
})
    .then(response => {
        if (!response.ok) {
            throw new Error("Invalid or expired token");
        }
        return response.json();
    })
    .then(data => {
        console.log("Token is valid:", data);
    })
    .catch(error => {
        console.error("Token validation failed:", error);
        window.location.href = "/login";
    });

const ws = new WebSocket(`ws://localhost:5015/api/chat/ws?token=${token}`);

ws.onopen = function () {
    console.log("Connected to WebSocket");
};

ws.onmessage = function (event) {
    try {
        const data = JSON.parse(event.data); // Парсим JSON

        if (data.type === "history") {
            data.messages.forEach(msg => appendMessage(msg.role, msg.content));
        } else {
            appendMessage(data.role, data.content);
        }
    } catch (e) {
        console.error("Ошибка парсинга WebSocket-сообщения:", e, event.data);
    }
};

function appendMessage(role, content) {
    const messageBox = document.getElementById("chat-box");
    const messageElement = document.createElement("div");

    // Убираем лишние символы у ассистента
    if (role === "assistant" && content.startsWith(":")) {
        content = content.substring(1).trim();
    }

    messageElement.innerHTML = `<strong>${role === "user" ? "Вы" : "Ассистент"}:</strong> ${content}`;
    messageElement.classList.add("message");
    
    messageBox.appendChild(messageElement);
    messageBox.scrollTop = messageBox.scrollHeight; // Автоскролл вниз
}



ws.onerror = function (event) {
    console.error("WebSocket error:", event);
    alert("WebSocket connection error. Please try again.");
};

ws.onclose = function () {
    console.log("WebSocket connection closed");
};

// Отправка сообщений
document.getElementById("message-form").addEventListener("submit", function (event) {
    event.preventDefault();
    const messageInput = document.getElementById("message-input");
    const message = messageInput.value.trim();

    if (message) {
        appendMessage("user", message); // Добавляем в чат сразу
        ws.send(message); // Отправка сообщения на сервер
        messageInput.value = ""; // Очистка поля ввода
    }
});


// Очистка чата
document.getElementById("clear-chat").addEventListener("click", async function () {
    const token = localStorage.getItem("access_token");
    if (!token) {
        alert("You are not authenticated!");
        return;
    }

    try {
        const response = await fetch("/api/chat/clear_chat", {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            }
        });

        if (!response.ok) {
            throw new Error("Failed to clear chat");
        }

        alert("Chat cleared!");
        document.getElementById("chat-box").innerHTML = ""; // Очистка чата на клиенте
    } catch (error) {
        console.error(error);
        alert("An error occurred");
    }
});

// Функция для отображения сообщений в чате
function displayMessage(role, content) {
    const chatBox = document.getElementById("chat-box");
    const messageElement = document.createElement("div");
    messageElement.classList.add("message", role);
    messageElement.textContent = content;
    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight; // Автопрокрутка вниз
}
