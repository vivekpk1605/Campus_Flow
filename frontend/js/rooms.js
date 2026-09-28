const token = window.CampusFlow?.token;

document.getElementById('roomForm')?.addEventListener('submit', async (event) => {
  event.preventDefault();
  const message = document.getElementById('roomMessage');
  try {
    const response = await fetch('/api/rooms', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify({
        room_number: document.getElementById('roomNumber').value.trim(),
        building: document.getElementById('building').value.trim(),
        floor: document.getElementById('floor').value,
        room_type: document.getElementById('roomType').value.trim(),
        capacity: document.getElementById('capacity').value,
        facilities: document.getElementById('facilities').value.trim()
      })
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.message || 'Unable to add room');
    message.textContent = 'Room added.';
    event.target.reset();
    loadRooms();
  } catch (error) {
    message.textContent = error.message;
  }
});

async function loadRooms() {
  const container = document.getElementById('roomsList');
  if (!container) return;

  try {
    const response = await fetch('http://localhost:5000/api/rooms', {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.message || 'Unable to fetch rooms');

    container.innerHTML = (result.rooms || []).map(room => `
      <div class="list-item">
        <h3>${room.room_number}</h3>
        <p>${room.building} • Floor ${room.floor}</p>
        <p>Type: ${room.room_type} • Capacity: ${room.capacity}</p>
        <p>Status: ${room.status}</p>
      </div>
    `).join('') || '<p>No rooms available.</p>';
  } catch (error) {
    container.innerHTML = `<p>${error.message}</p>`;
  }
}

loadRooms();
