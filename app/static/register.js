document.getElementById("register-form").addEventListener("submit", async function(event) {
    event.preventDefault();

    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();

    if (!username || !password) {
        alert("Заполните все поля!");
        return;
    }

    try {
        const response = await fetch("/api/auth/register", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Ошибка регистрации");
        }

        alert("Регистрация успешна!");
        localStorage.setItem("access_token", data.access_token);
        window.location.href = "/chat";
    } catch (error) {
        alert(error.message);
    }
});
