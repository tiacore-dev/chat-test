const token = localStorage.getItem("access_token");

if (!token) {
    console.error("Token not found in localStorage");
    window.location.href = "/";
}

// Загружаем пользователей
async function loadUsers() {
    try {
        const response = await fetch("/admin/users", {
            headers: { "Authorization": `Bearer ${token}` }
        });
        const users = await response.json();

        const usersList = document.getElementById("users-list");
        usersList.innerHTML = "";
        users.forEach(user => {
            usersList.innerHTML += `
                <tr>
                    <td>${user.user_id}</td>
                    <td>${user.username}</td>
                    <td>${user.role}</td>
                    <td>
                        <button class="btn btn-sm btn-danger" onclick="blockUser('${user.user_id}')">Заблокировать</button>
                        <button class="btn btn-sm btn-warning" onclick="deleteUser('${user.user_id}')">Удалить</button>
                    </td>
                </tr>`;
        });
    } catch (error) {
        console.error("Error loading users:", error);
    }
}

// Заблокировать пользователя
async function blockUser(userId) {
    try {
        await fetch(`/admin/users/${userId}/block`, {
            method: "POST",
            headers: { "Authorization": `Bearer ${token}` }
        });
        alert("Пользователь заблокирован!");
        loadUsers();
    } catch (error) {
        console.error("Error blocking user:", error);
    }
}

// Удалить пользователя
async function deleteUser(userId) {
    try {
        await fetch(`/admin/users/${userId}`, {
            method: "DELETE",
            headers: { "Authorization": `Bearer ${token}` }
        });
        alert("Пользователь удален!");
        loadUsers();
    } catch (error) {
        console.error("Error deleting user:", error);
    }
}

// Загружаем и фильтруем логи
async function loadLogs() {
    const levelFilter = document.getElementById("log-level").value; // Получаем уровень логов
    const dateFilter = document.getElementById("log-date").value; // Получаем дату

    try {
        const response = await fetch("/admin/logs", {
            headers: { "Authorization": `Bearer ${token}` }
        });

        if (!response.ok) {
            throw new Error("Failed to fetch logs");
        }

        const logs = await response.text();
        const logsContainer = document.getElementById("logs-container");
        logsContainer.innerHTML = ""; // Очистка перед загрузкой новых данных

        const lines = logs.split("\n"); // Разделяем логи по строкам
        let filteredLogs = lines.filter(line => {
            if (!line.trim()) return false; // Пропускаем пустые строки

            // Фильтр по дате (если выбран)
            if (dateFilter) {
                const logDate = line.substring(0, 10); // Берём дату из лога (YYYY-MM-DD)
                if (!logDate.startsWith(dateFilter)) return false;
            }

            // Фильтр по уровню логирования
            if (levelFilter !== "ALL" && !line.includes(levelFilter)) return false;

            return true;
        });

        // Выводим отфильтрованные логи
        filteredLogs.forEach(line => {
            const logLine = document.createElement("div");
            logLine.textContent = line;
            logLine.classList.add("log-line");
            logsContainer.appendChild(logLine);
        });

        logsContainer.scrollTop = logsContainer.scrollHeight; // Прокрутка вниз
    } catch (error) {
        console.error("Ошибка загрузки логов:", error);
    }
}

// Обновляем логи при изменении фильтра
document.getElementById("log-level").addEventListener("change", loadLogs);
document.getElementById("log-date").addEventListener("change", loadLogs);

// Загружаем логи при загрузке страницы
window.addEventListener("load", loadLogs);


// Загружаем активные WebSocket-подключения
async function loadConnections() {
    try {
        const response = await fetch("/admin/connections", {
            headers: { "Authorization": `Bearer ${token}` }
        });
        const connections = await response.json();

        const connectionsList = document.getElementById("connections-list");
        connectionsList.innerHTML = "";
        connections.forEach(conn => {
            connectionsList.innerHTML += `<li class="list-group-item">${conn.user} (IP: ${conn.ip})</li>`;
        });
    } catch (error) {
        console.error("Error loading connections:", error);
    }
}

// Сохранение настроек
document.getElementById("save-settings").addEventListener("click", async function () {
    const messageLimit = document.getElementById("message-limit").value;
    const tokenExpiry = document.getElementById("token-expiry").value;

    try {
        await fetch("/admin/settings", {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message_limit: messageLimit, token_expiry: tokenExpiry })
        });
        alert("Настройки сохранены!");
    } catch (error) {
        console.error("Error saving settings:", error);
    }
});

// Инициализация загрузки данных
document.addEventListener("DOMContentLoaded", () => {
    loadUsers();
    loadLogs();
    loadConnections();
});

document.getElementById("back-to-chat").addEventListener("click", () => {
    window.location.href = "/chat";
});
