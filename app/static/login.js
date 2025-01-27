document.getElementById("login-form").addEventListener("submit", async function (event) {
    event.preventDefault(); // Предотвращаем стандартное поведение формы

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    try {
        // Отправляем запрос на сервер для получения токена
        const response = await fetch("/api/auth/token", {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: new URLSearchParams({ username, password }),
        });

        if (response.ok) {
            const data = await response.json();
            // Сохраняем токен в localStorage
            localStorage.setItem("access_token", data.access_token);
            // Перенаправляем пользователя на страницу чата
            window.location.href = "/chat";
        } else {
            alert("Invalid credentials, please try again.");
        }
    } catch (error) {
        console.error("Error during login:", error);
        alert("Something went wrong, please try again.");
    }
});
