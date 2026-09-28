const token = window.CampusFlow?.token;
const isAdmin = window.CampusFlow?.user?.role === 'ADMIN';

function readFile(file) {
  return new Promise((resolve, reject) => {
    if (!file) return resolve(null);
    if (file.size > 5 * 1024 * 1024) return reject(new Error('File must be 5 MB or smaller.'));
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = () => reject(new Error('Unable to read file.'));
    reader.readAsDataURL(file);
  });
}

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>'"]/g, (character) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
  }[character]));
}

// Reads a response as JSON, and explains clearly when the server sent HTML instead.
async function parseJson(response) {
  const raw = await response.text();
  try {
    return JSON.parse(raw);
  } catch (_) {
    if (response.status === 413) {
      throw new Error('The attached file is too large for the server. Try a smaller file.');
    }
    throw new Error(`Server returned ${response.status} ${response.statusText} (not JSON) for ${response.url}`);
  }
}

async function submitRequest(endpoint, payload, messageId, form) {
  const message = document.getElementById(messageId);
  message.className = 'message';
  message.textContent = 'Submitting…';
  try {
    if (!token) throw new Error('You are not logged in. Please log in again.');
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify(payload)
    });
    const result = await parseJson(response);
    if (!response.ok) throw new Error(result.message || 'Unable to submit request');
    message.textContent = 'Request submitted and sent for admin review.';
    message.className = 'message success';
    form.reset();
    loadRequests();
  } catch (error) {
    message.textContent = error.message;
    message.className = 'message error';
  }
}

document.getElementById('odForm')?.addEventListener('submit', async (event) => {
  event.preventDefault();
  const message = document.getElementById('odMessage');
  try {
    const startDate = document.getElementById('odStartDate').value;
    const endDate = document.getElementById('odEndDate').value;
    if (endDate < startDate) throw new Error('The end date must be on or after the start date.');
    const evidence = await readFile(document.getElementById('odEvidence').files[0]);
    await submitRequest('/api/requests/od', {
      purpose: document.getElementById('odPurpose').value.trim(),
      destination: document.getElementById('odDestination').value.trim(),
      start_date: startDate,
      end_date: endDate,
      details: document.getElementById('odDetails').value.trim(),
      evidence
    }, 'odMessage', event.target);
  } catch (error) {
    message.textContent = error.message;
    message.className = 'message error';
  }
});

document.getElementById('leaveForm')?.addEventListener('submit', async (event) => {
  event.preventDefault();
  const message = document.getElementById('leaveMessage');
  try {
    const startDate = document.getElementById('leaveStartDate').value;
    const endDate = document.getElementById('leaveEndDate').value;
    if (endDate < startDate) throw new Error('The end date must be on or after the start date.');
    const evidence = await readFile(document.getElementById('leaveEvidence').files[0]);
    await submitRequest('/api/requests/leave', {
      reason: document.getElementById('leaveReason').value.trim(),
      start_date: startDate,
      end_date: endDate,
      details: document.getElementById('leaveDetails').value.trim(),
      evidence
    }, 'leaveMessage', event.target);
  } catch (error) {
    message.textContent = error.message;
    message.className = 'message error';
  }
});

async function reviewRequest(type, requestId, status) {
  try {
    const response = await fetch(`/api/requests/${type}/${requestId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({ status })
    });
    if (response.ok) loadRequests();
    else {
      const result = await parseJson(response);
      alert(result.message || 'Unable to update request.');
    }
  } catch (error) {
    alert(error.message);
  }
}

function requestMarkup(item, type) {
  const title = type === 'od' ? item.purpose : item.reason;
  const extra = type === 'od' ? `Destination: ${item.destination}` : 'Leave permission';
  const actions = isAdmin && item.status === 'Pending' ? `
    <button class="btn primary" onclick="reviewRequest('${type}', ${item.request_id}, 'Approved')">Approve &amp; sign</button>
    <button class="btn danger" onclick="reviewRequest('${type}', ${item.request_id}, 'Rejected')">Reject</button>
  ` : '';
  return `<div class="list-item request-item">
    <h3>${escapeHtml(title)}</h3>
    ${isAdmin ? `<p><strong>Requester:</strong> ${escapeHtml(item.user_name)} (${escapeHtml(item.user_role)})</p>` : ''}
    <p>${escapeHtml(extra)} · ${escapeHtml(item.start_date)} to ${escapeHtml(item.end_date)}</p>
    <p>${escapeHtml(item.details)}</p>
    <p><strong>Status:</strong> ${escapeHtml(item.status)} ${item.digital_signature ? `· ${escapeHtml(item.digital_signature)}` : ''}</p>
    <div class="request-actions">${actions}</div>
  </div>`;
}

async function loadRequests() {
  const container = document.getElementById('requestList');
  if (!container) return;
  try {
    const [odResponse, leaveResponse] = await Promise.all([
      fetch('/api/requests/od', { headers: { Authorization: `Bearer ${token}` } }),
      fetch('/api/requests/leave', { headers: { Authorization: `Bearer ${token}` } })
    ]);
    const od = await parseJson(odResponse);
    const leave = await parseJson(leaveResponse);
    const items = [
      ...(od.requests || []).map((item) => requestMarkup(item, 'od')),
      ...(leave.requests || []).map((item) => requestMarkup(item, 'leave'))
    ];
    container.innerHTML = items.join('') || '<p>No requests submitted yet.</p>';
  } catch (error) {
    container.innerHTML = `<p class="message error">${escapeHtml(error.message)}</p>`;
  }
}

if (isAdmin) {
  document.getElementById('requestForms')?.remove();
  document.getElementById('requestListTitle').textContent = 'Requests awaiting review';
}

loadRequests();