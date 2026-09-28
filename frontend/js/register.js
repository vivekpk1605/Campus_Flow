const registerForm = document.getElementById('registerForm');
const messageBox = document.getElementById('registerMessage');

registerForm?.addEventListener('submit', async (event) => {
  event.preventDefault();
  messageBox.textContent = 'Creating account...';

  const payload = {
    name: document.getElementById('name').value.trim(),
    email: document.getElementById('email').value.trim(),
    password: document.getElementById('password').value,
    role: document.getElementById('role').value,
    phone: document.getElementById('phone').value.trim()
  };

  try {
    const response = await fetch('/api/auth/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });

    const result = await response.json();
    if (!response.ok) {
      throw new Error(result.message || 'Registration failed');
    }

    messageBox.textContent = 'Account created. Redirecting to login...';
    window.setTimeout(() => {
      window.location.href = 'login.html';
    }, 800);
  } catch (error) {
    messageBox.textContent = error.message;
  }
});
