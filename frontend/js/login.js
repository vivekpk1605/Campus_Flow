const loginForm = document.getElementById('loginForm');
const messageBox = document.getElementById('loginMessage');

loginForm?.addEventListener('submit', async (event) => {
  event.preventDefault();
  const email = document.getElementById('email').value.trim();
  const password = document.getElementById('password').value;

  messageBox.textContent = 'Signing in...';

  try {
    const response = await fetch('http://localhost:5000/api/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ email, password })
    });

    const result = await response.json();
    if (!response.ok) {
      throw new Error(result.message || 'Login failed');
    }

    localStorage.setItem('campusflow_token', result.token);
    localStorage.setItem('campusflow_user', JSON.stringify(result.user));
    messageBox.textContent = 'Login successful';

    const role = result.user.role;
    if (role === 'ADMIN') {
      window.location.href = 'admin-dashboard.html';
    } else if (role === 'FACULTY') {
      window.location.href = 'faculty-dashboard.html';
    } else {
      window.location.href = 'student-dashboard.html';
    }
  } catch (error) {
    messageBox.textContent = error.message;
  }
});
