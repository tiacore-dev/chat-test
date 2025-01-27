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
        window.location.href = "/";
    });



const ws = new WebSocket(`ws://localhost:5015/api/chat/ws?token=${token}`);

ws.onopen = function () {
    console.log("Connected to WebSocket");
};

ws.onmessage = function (event) {
    const message = document.createElement("div");
    message.textContent = event.data; // Сообщение от сервера
    document.getElementById("chat-box").appendChild(message);
};

ws.onerror = function (event) {
    console.error("WebSocket error:", event);
    alert("WebSocket connection error. Please try again.");
};

ws.onclose = function () {
    console.log("WebSocket connection closed");
};

document.getElementById("message-form").addEventListener("submit", function (event) {
    event.preventDefault();
    const message = document.getElementById("message-input").value;

    if (message) {
        ws.send(message); // Отправка сообщения на сервер
        document.getElementById("message-input").value = ""; // Очистка поля ввода
    }
});