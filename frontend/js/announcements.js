const token = window.CampusFlow?.token;

document.getElementById('announcementForm')?.addEventListener('submit', async (event) => {
  event.preventDefault();
  const message = document.getElementById('announcementMessage');
  try {
    const response = await fetch('/api/announcements', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({
        title: document.getElementById('announcementTitle').value.trim(),
        description: document.getElementById('announcementDescription').value.trim(),
        category: document.getElementById('announcementCategory').value.trim()
      })
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.message || 'Unable to publish announcement');
    message.textContent = 'Announcement published.';
    event.target.reset();
    loadAnnouncements();
  } catch (error) {
    message.textContent = error.message;
  }
});

async function loadAnnouncements() {
  const container = document.getElementById('announcementsList');
  if (!container) return;

  try {
    const response = await fetch('http://localhost:5000/api/announcements', {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.message || 'Unable to fetch announcements');

    container.innerHTML = (result.announcements || []).map(item => `
      <div class="list-item">
        <h3>${item.title}</h3>
        <p>${item.description}</p>
        <p><strong>Category:</strong> ${item.category} • <strong>Status:</strong> ${item.status}</p>
      </div>
    `).join('') || '<p>No announcements yet.</p>';
  } catch (error) {
    container.innerHTML = `<p>${error.message}</p>`;
  }
}

loadAnnouncements();
