const token = window.CampusFlow?.token;
const userRole = window.CampusFlow?.user?.role;
const isAdmin = userRole === 'ADMIN';

function readEvidence(file) {
  return new Promise((resolve, reject) => {
    if (!file) return resolve(null);
    if (file.size > 5 * 1024 * 1024) return reject(new Error('Evidence file must be 5 MB or smaller.'));
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = () => reject(new Error('Unable to read evidence file.'));
    reader.readAsDataURL(file);
  });
}

if (isAdmin) {
  document.getElementById('complaintFormPanel')?.remove();
  const heading = document.getElementById('complaintsHeading');
  if (heading) heading.textContent = 'All submitted complaints';
}

document.getElementById('complaintForm')?.addEventListener('submit', async (event) => {
  event.preventDefault();
  const message = document.getElementById('complaintMessage');
  message.textContent = 'Submitting...';

  try {
    const evidence = await readEvidence(document.getElementById('complaintEvidence').files[0]);
    const response = await fetch('/api/complaints', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({
        category: document.getElementById('category').value,
        title: document.getElementById('title').value.trim(),
        description: document.getElementById('description').value.trim(),
        location: document.getElementById('location').value.trim(),
        image: evidence
      })
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.message || 'Unable to submit complaint');
    message.textContent = 'Complaint submitted successfully.';
    event.target.reset();
    loadComplaints();
  } catch (error) {
    message.textContent = error.message;
  }
});

async function loadComplaints() {
  const container = document.getElementById('complaintsList');
  if (!container) return;

  try {
    const endpoint = isAdmin ? '/api/complaints' : '/api/complaints/my';
    const response = await fetch(endpoint, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.message || 'Unable to fetch complaints');

    container.innerHTML = (result.complaints || []).map(item => `
      <div class="list-item">
        <h3>${item.title}</h3>
        <p>${item.description}</p>
        ${isAdmin ? `<p><strong>Submitted by:</strong> ${item.user_name || 'Unknown'} (${item.user_role || 'User'}) · ${item.user_email || ''}</p>` : ''}
        <p><strong>Location:</strong> ${item.location || 'Campus'}</p>
        <p><strong>Category:</strong> ${item.category} • <strong>Status:</strong> ${item.status}</p>
      </div>
    `).join('') || '<p>No complaints reported yet.</p>';
  } catch (error) {
    container.innerHTML = `<p>${error.message}</p>`;
  }
}

loadComplaints();
