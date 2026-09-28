const storedUser = JSON.parse(localStorage.getItem('campusflow_user') || 'null');

window.CampusFlow = {
  token: localStorage.getItem('campusflow_token'),
  user: storedUser,
  loginPath: 'login.html',
  getAuthHeaders() {
    return {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${this.token || ''}`
    };
  },
  dashboardPath(role) {
    if (role === 'ADMIN') return 'admin-dashboard.html';
    if (role === 'FACULTY') return 'faculty-dashboard.html';
    return 'student-dashboard.html';
  },
  requireAuth(expectedRole) {
    if (!this.token || !this.user) {
      window.location.href = this.loginPath;
      return false;
    }

    if (expectedRole && this.user.role !== expectedRole) {
      window.location.href = this.dashboardPath(this.user.role);
      return false;
    }

    return true;
  },
  async logout() {
    try {
      if (this.token) {
        await fetch('/api/auth/logout', {
          method: 'POST',
          headers: this.getAuthHeaders()
        });
      }
    } finally {
      localStorage.removeItem('campusflow_token');
      localStorage.removeItem('campusflow_user');
      window.location.href = this.loginPath;
    }
  }
};

window.logout = () => window.CampusFlow.logout();

window.CampusFlow.requireAuth(document.body.dataset.role || null);

// Campus AI is available as a compact assistant on authenticated pages.
if (window.CampusFlow.token && window.CampusFlow.user) {
  const aiScript = document.createElement('script');
  aiScript.src = 'js/ai-widget.js';
  document.body.appendChild(aiScript);
}

document.querySelectorAll('[data-roles]').forEach((element) => {
  const allowedRoles = element.dataset.roles.split(',');
  if (!allowedRoles.includes(window.CampusFlow.user?.role)) element.remove();
});

document.querySelectorAll('a').forEach((link) => {
  if (link.textContent.trim() === 'Dashboard') {
    link.href = window.CampusFlow.dashboardPath(window.CampusFlow.user?.role);
  }

  const currentPage = window.location.pathname.split('/').pop();
  if (link.getAttribute('href') === currentPage) link.classList.add('active');
});

const profile = document.querySelector('.topbar');
if (profile && window.CampusFlow.user) {
  const userBadge = document.createElement('div');
  userBadge.className = 'user-badge';
  userBadge.innerHTML = `
    <span class="user-avatar">${window.CampusFlow.user.name.charAt(0).toUpperCase()}</span>
    <span><strong>${window.CampusFlow.user.name}</strong><small>${window.CampusFlow.user.role}</small></span>
  `;
  profile.appendChild(userBadge);
}
