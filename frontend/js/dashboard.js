const token = window.CampusFlow?.token;

function getAuthHeaders() {
  return {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${token}`
  };
}

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>'"]/g, (character) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
  }[character]));
}

function drawChart(canvas, values, labels, color, type) {
  if (!canvas) return;
  const context = canvas.getContext('2d');
  const ratio = window.devicePixelRatio || 1;
  const width = canvas.clientWidth || 640;
  const height = 260;
  canvas.width = width * ratio;
  canvas.height = height * ratio;
  context.setTransform(ratio, 0, 0, ratio, 0, 0);
  context.clearRect(0, 0, width, height);

  const padding = { top: 24, right: 24, bottom: 48, left: 34 };
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;
  const maximum = Math.max(...values, 1);

  context.strokeStyle = '#d7e2eb';
  context.lineWidth = 1;
  for (let step = 0; step <= 4; step += 1) {
    const y = padding.top + (chartHeight / 4) * step;
    context.beginPath();
    context.moveTo(padding.left, y);
    context.lineTo(width - padding.right, y);
    context.stroke();
  }

  context.font = '12px Arial';
  context.fillStyle = '#64748b';
  context.textAlign = 'center';
  const positions = values.map((value, index) => ({
    x: padding.left + (chartWidth / Math.max(values.length - 1, 1)) * index,
    y: padding.top + chartHeight - (value / maximum) * chartHeight
  }));

  if (type === 'line') {
    context.strokeStyle = color;
    context.lineWidth = 4;
    context.lineJoin = 'round';
    context.beginPath();
    positions.forEach((point, index) => {
      if (index === 0) context.moveTo(point.x, point.y);
      else context.lineTo(point.x, point.y);
    });
    context.stroke();
    positions.forEach((point, index) => {
      context.fillStyle = '#ffffff';
      context.beginPath();
      context.arc(point.x, point.y, 6, 0, Math.PI * 2);
      context.fill();
      context.fillStyle = color;
      context.beginPath();
      context.arc(point.x, point.y, 4, 0, Math.PI * 2);
      context.fill();
      context.fillStyle = '#17324d';
      context.fillText(String(values[index]), point.x, point.y - 14);
    });
  } else {
    const barWidth = Math.min(54, chartWidth / values.length / 2);
    positions.forEach((point, index) => {
      const barHeight = (values[index] / maximum) * chartHeight;
      const x = point.x - barWidth / 2;
      const y = padding.top + chartHeight - barHeight;
      context.fillStyle = color;
      context.fillRect(x, y, barWidth, barHeight);
      context.fillStyle = '#17324d';
      context.fillText(String(values[index]), point.x, y - 8);
    });
  }

  labels.forEach((label, index) => {
    context.fillStyle = '#64748b';
    context.fillText(label, positions[index].x, height - 16);
  });
}

function renderAdminCharts(analytics) {
  drawChart(
    document.getElementById('complaintsChart'),
    [analytics.total_complaints, analytics.active_complaints, analytics.resolved_complaints],
    ['Total', 'Active', 'Resolved'],
    '#e05d3f',
    'line'
  );
  drawChart(
    document.getElementById('resourcesChart'),
    [analytics.total_students, analytics.total_faculty, analytics.total_rooms],
    ['Students', 'Faculty', 'Rooms'],
    '#2c7a7b',
    'bar'
  );
}

async function loadDashboardData() {
  window.CampusFlow.requireAuth();

  const dashboardData = document.getElementById('dashboardData');
  const studentsCount = document.getElementById('studentsCount');
  const facultyCount = document.getElementById('facultyCount');
  const complaintsCount = document.getElementById('complaintsCount');
  const roomsCount = document.getElementById('roomsCount');
  const overview = document.getElementById('studentOverview');

  try {
    const response = window.CampusFlow.user?.role === 'ADMIN'
      ? await fetch('/api/analytics', { headers: getAuthHeaders() })
      : null;

    if (response?.ok) {
      const result = await response.json();
      if (dashboardData) {
        const analytics = result.analytics;
        renderAdminCharts(analytics);
        dashboardData.innerHTML = `
          <div class="metric-groups">
            <section class="metric-group">
              <h3>People</h3>
              <div class="metric-grid">
                <div class="metric"><span>Total users</span><strong>${analytics.total_users}</strong></div>
                <div class="metric"><span>Students</span><strong>${analytics.total_students}</strong></div>
                <div class="metric"><span>Faculty</span><strong>${analytics.total_faculty}</strong></div>
              </div>
            </section>
            <section class="metric-group">
              <h3>Campus operations</h3>
              <div class="metric-grid">
                <div class="metric"><span>Total rooms</span><strong>${analytics.total_rooms}</strong></div>
                <div class="metric"><span>Available rooms</span><strong>${analytics.available_rooms}</strong></div>
              </div>
            </section>
            <section class="metric-group">
              <h3>Complaint activity</h3>
              <div class="metric-grid">
                <div class="metric"><span>Total complaints</span><strong>${analytics.total_complaints}</strong></div>
                <div class="metric"><span>Active complaints</span><strong>${analytics.active_complaints}</strong></div>
                <div class="metric"><span>Resolved complaints</span><strong>${analytics.resolved_complaints}</strong></div>
              </div>
            </section>
            <section class="metric-group">
              <h3>Lost and found</h3>
              <div class="metric-grid">
                <div class="metric"><span>Lost items</span><strong>${analytics.lost_items}</strong></div>
                <div class="metric"><span>Found items</span><strong>${analytics.found_items}</strong></div>
              </div>
            </section>
          </div>
        `;
      }
      if (studentsCount) studentsCount.textContent = result.analytics.total_students || 0;
      if (facultyCount) facultyCount.textContent = result.analytics.total_faculty || 0;
      if (complaintsCount) complaintsCount.textContent = result.analytics.active_complaints || 0;
      if (roomsCount) roomsCount.textContent = result.analytics.total_rooms || 0;
    }

    if (window.CampusFlow.user?.role === 'ADMIN') {
      const [usersResponse, complaintsResponse] = await Promise.all([
        fetch('/api/users', { headers: getAuthHeaders() }),
        fetch('/api/complaints', { headers: getAuthHeaders() })
      ]);
      const usersResult = await usersResponse.json();
      const complaintsResult = await complaintsResponse.json();
      const userDirectory = document.getElementById('userDirectory');
      const complaintPreview = document.getElementById('adminComplaintPreview');

      if (userDirectory) {
        userDirectory.innerHTML = (usersResult.users || []).map((user) => `
          <div class="directory-row">
            <strong>${escapeHtml(user.name)}</strong>
            <span>${escapeHtml(user.email)}</span>
            <span class="role-tag">${escapeHtml(user.role)}</span>
            <button class="btn danger delete-user" data-user-id="${user.user_id}" type="button">Delete</button>
          </div>
        `).join('') || '<p>No registered users yet.</p>';

        userDirectory.querySelectorAll('.delete-user').forEach((button) => {
          button.addEventListener('click', async () => {
            if (!window.confirm('Delete this user and their personal records?')) return;
            const response = await fetch(`/api/users/${button.dataset.userId}`, {
              method: 'DELETE',
              headers: getAuthHeaders()
            });
            if (response.ok) loadDashboardData();
          });
        });
      }

      if (complaintPreview) {
        complaintPreview.innerHTML = (complaintsResult.complaints || []).slice(0, 5).map((complaint) => `
          <div class="directory-row">
            <strong>${escapeHtml(complaint.title)}</strong>
            <span>${escapeHtml(complaint.user_name || 'Unknown')} - ${escapeHtml(complaint.location)}</span>
            <span class="role-tag">${escapeHtml(complaint.status)}</span>
          </div>
        `).join('') || '<p>No complaints submitted yet.</p>';
      }
    }

    if (window.CampusFlow.user?.role !== 'ADMIN') {
      const [announcementsResponse, roomsResponse, complaintsResponse] = await Promise.all([
        fetch('/api/announcements', { headers: getAuthHeaders() }),
        fetch('/api/rooms', { headers: getAuthHeaders() }),
        fetch('/api/complaints/my', { headers: getAuthHeaders() })
      ]);
      const announcements = await announcementsResponse.json();
      const rooms = await roomsResponse.json();
      const complaints = await complaintsResponse.json();
      const setCount = (id, value) => {
        const element = document.getElementById(id);
        if (element) element.textContent = value;
      };
      setCount('announcementCount', (announcements.announcements || []).length);
      setCount('roomCount', (rooms.rooms || []).length);
      setCount('complaintCount', (complaints.complaints || []).length);
    }

    if (overview) {
      overview.innerHTML = '<li>Live campus data is loaded from MySQL.</li>';
    }
  } catch (error) {
    console.error('Dashboard load failed', error);
  }
}

loadDashboardData();
