// Configuration
const API_BASE_URL = 'https://login-page-project-production.up.railway.app'; // Replace with your Railway URL

// DOM Elements
const loginForm = document.getElementById('loginForm');
const messageDiv = document.getElementById('message');

// Event Listeners
loginForm.addEventListener('submit', handleLogin);

// Functions
async function handleLogin(e) {
    e.preventDefault();

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    try {
        showMessage('Logging in...', 'info');

        const response = await fetch(`${API_BASE_URL}/api/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (response.ok) {
            showMessage('Login successful!', 'success');
            localStorage.setItem('token', data.token);
            // Redirect to dashboard or home page
            setTimeout(() => {
                window.location.href = 'dashboard.html';
            }, 1500);
        } else {
            showMessage(data.error || 'Login failed', 'error');
        }
    } catch (error) {
        showMessage('Network error. Please try again.', 'error');
        console.error('Login error:', error);
    }
}

function showMessage(text, type) {
    messageDiv.textContent = text;
    messageDiv.className = `message ${type}`;
    messageDiv.style.display = 'block';

    if (type === 'success') {
        setTimeout(() => {
            messageDiv.style.display = 'none';
        }, 3000);
    }
}// JavaScript source code
