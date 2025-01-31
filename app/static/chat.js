const token = localStorage.getItem("access_token");

if (!token) {
    console.error("Token not found in localStorage");
    window.location.href = "/";
}

// Глобальная переменная для WebSocket
let ws;

// Функция для проверки роли пользователя
function checkUserRole() {
    return fetch("/api/user/me", {
        method: "GET",
        headers: { "Authorization": `Bearer ${token}` }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Failed to fetch user data");
        }
        return response.json();
    })
    .then(user => {
        console.log("User data:", user); // Логируем ответ API
        if (user.role === "admin") {
            console.log("User is admin, showing admin panel button.");
            document.getElementById("admin-panel").style.display = "inline-block";
        }
    })
    .catch(error => {
        console.error("Error fetching user data:", error);
        window.location.href = "/";
    });
}

// Функция для проверки токена и установки WebSocket
function initializeWebSocket() {
    return fetch("/protected", {
        method: "GET",
        headers: { "Authorization": `Bearer ${token}` }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Invalid or expired token");
        }
        return response.json();
    })
    .then(data => {
        console.log("Token is valid:", data);
        return fetch("/config"); // Запрос на получение WebSocket URL
    })
    .then(response => response.json())
    .then(config => {
        ws = new WebSocket(`${config.ws_url}?token=${token}`);
        console.log("WebSocket connected to:", config.ws_url);

        ws.onopen = function () {
            console.log("Connected to WebSocket");
        };

        ws.onmessage = function (event) {
            try {
                const data = JSON.parse(event.data);

                if (data.error) {
                    alert(data.error); // Выводим ошибку на экран
                    ws.close(); // Закрываем соединение
                    return;
                }

                if (data.type === "history") {
                    data.messages.forEach(msg => appendMessage(msg.role, msg.content));
                } else {
                    appendMessage(data.role, data.content);
                }
            } catch (e) {
                console.error("Ошибка парсинга WebSocket-сообщения:", e, event.data);
            }
        };


        ws.onerror = function (event) {
            console.error("WebSocket error:", event);
            alert("WebSocket connection error. Please try again.");
        };

        ws.onclose = function () {
            console.log("WebSocket connection closed");
        };
    })
    .catch(error => {
        console.error("Failed to fetch WebSocket config:", error);
        window.location.href = "/";
    });
}

// Функция для отображения сообщений в чате
function appendMessage(role, content) {
    const messageBox = document.getElementById("chat-box");
    const messageElement = document.createElement("div");

    // Очищаем контент ассистента от лишних символов
    if (role === "assistant") {
        content = content.replace(/^[:#]+/, "").trim(); // Убираем ":" и "###"
    }

    messageElement.innerHTML = `<strong>${role === "user" ? "Вы" : "Ассистент"}:</strong> ${content}`;
    messageElement.classList.add("message");

    messageBox.appendChild(messageElement);
    messageBox.scrollTop = messageBox.scrollHeight; // Автоскролл вниз
}

// Инициализация WebSocket и проверка роли пользователя
Promise.all([checkUserRole(), initializeWebSocket()])
    .then(() => console.log("Initialization complete"))
    .catch(error => console.error("Initialization failed:", error));

// Отправка сообщений
document.getElementById("message-form").addEventListener("submit", function (event) {
    event.preventDefault();
    const messageInput = document.getElementById("message-input");
    const message = messageInput.value.trim();

    if (message) {
        ws.send(message); // ✅ Отправка на сервер
        messageInput.value = ""; // Очистка поля ввода
    }
});

// Очистка чата
document.getElementById("clear-chat").addEventListener("click", async function () {
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

// Кнопка "Выйти"
document.getElementById("logout").addEventListener("click", function () {
    localStorage.removeItem("access_token");
    window.location.href = "/";
});

// Переход в админку
document.getElementById("admin-panel").addEventListener("click", () => {
    window.location.href = "/admin";
});
