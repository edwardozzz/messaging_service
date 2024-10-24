document.getElementById('register-button').addEventListener('click', async () => {
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;
    const username = document.getElementById('register-username').value; // Добавьте эту строку

    const response = await fetch('http://localhost:8000/register/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, password, username }) // Включите username
    });

    if (response.ok) {
        alert('Регистрация успешна');
    } else {
        alert('Ошибка регистрации');
    }
});

document.getElementById('login-button').addEventListener('click', async () => {
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;

    const response = await fetch('http://localhost:8000/login/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
    });

    if (response.ok) {
        const data = await response.json();
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('userId', data.user_id);
        window.location.href = 'chat.html';
    } else {
        alert('Ошибка входа');
    }
});
