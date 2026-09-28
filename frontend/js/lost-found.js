const token = window.CampusFlow?.token;

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

document.getElementById('lostFoundForm')?.addEventListener('submit', async (event) => {
  event.preventDefault();
  const message = document.getElementById('lostFoundMessage');
  message.textContent = 'Submitting...';

  try {
    const itemType = document.getElementById('itemType').value;
    const evidence = await readEvidence(document.getElementById('lostFoundEvidence').files[0]);
    const response = await fetch('/api/lost-found', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({
        item_type: itemType,
        item_name: document.getElementById('itemName').value.trim(),
        description: document.getElementById('itemDescription').value.trim(),
        category: document.getElementById('itemCategory').value.trim(),
        location: document.getElementById('itemLocation').value.trim(),
        date_lost: itemType === 'Lost' ? document.getElementById('itemDate').value : null,
        date_found: itemType === 'Found' ? document.getElementById('itemDate').value : null,
        contact_information: document.getElementById('contactInformation').value.trim(),
        image: evidence
      })
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.message || 'Unable to submit report');
    message.textContent = 'Lost-and-found report submitted.';
    event.target.reset();
    loadLostFound();
  } catch (error) {
    message.textContent = error.message;
  }
});

async function loadLostFound() {
  const container = document.getElementById('lostFoundList');
  if (!container) return;

  try {
    const response = await fetch('http://localhost:5000/api/lost-found', {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.message || 'Unable to fetch records');

    container.innerHTML = (result.items || []).map(item => `
      <div class="list-item">
        <h3>${item.item_name}</h3>
        <p>${item.description}</p>
        <p><strong>Type:</strong> ${item.item_type} • <strong>Status:</strong> ${item.status}</p>
      </div>
    `).join('') || '<p>No lost or found records.</p>';
  } catch (error) {
    container.innerHTML = `<p>${error.message}</p>`;
  }
}

loadLostFound();
