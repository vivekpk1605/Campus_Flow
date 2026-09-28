(() => {
  const launcher = document.createElement('button');
  launcher.className = 'ai-launcher';
  launcher.type = 'button';
  launcher.setAttribute('aria-label', 'Open Campus AI assistant');
  launcher.setAttribute('aria-expanded', 'false');
  launcher.innerHTML = '<span aria-hidden="true">✦</span>';

  const panel = document.createElement('aside');
  panel.className = 'ai-panel';
  panel.setAttribute('aria-label', 'Campus AI assistant');
  panel.setAttribute('aria-hidden', 'true');
  panel.innerHTML = `
    <div class="ai-panel-header">
      <div><span class="ai-brand">✦ Campus AI</span><small>Gemini-powered assistance</small></div>
      <button class="ai-close" type="button" aria-label="Close Campus AI">×</button>
    </div>
    <div class="ai-messages" role="log" aria-live="polite">
      <div class="ai-bubble assistant">Hello! Ask me about OD forms, leave permission, complaints, or campus services.</div>
    </div>
    <form class="ai-form">
      <input aria-label="Message Campus AI" placeholder="Ask a campus question…" autocomplete="off" required />
      <button class="btn primary" type="submit" aria-label="Send message">Send</button>
    </form>`;

  document.body.append(launcher, panel);

  const messages = panel.querySelector('.ai-messages');
  const form = panel.querySelector('.ai-form');
  const input = form.querySelector('input');
  const sendButton = form.querySelector('button[type="submit"]');
  const closeButton = panel.querySelector('.ai-close');

  function setOpen(open) {
    panel.classList.toggle('open', open);
    launcher.classList.toggle('open', open);
    panel.setAttribute('aria-hidden', String(!open));
    launcher.setAttribute('aria-expanded', String(open));
    if (open) input.focus();
  }

  // Returns the bubble so callers can update it later.
  function addMessage(text, role) {
    const bubble = document.createElement('div');
    bubble.className = `ai-bubble ${role}`;
    bubble.textContent = text;
    messages.appendChild(bubble);
    messages.scrollTop = messages.scrollHeight;
    return bubble;
  }

  launcher.addEventListener('click', () => setOpen(!panel.classList.contains('open')));
  closeButton.addEventListener('click', () => setOpen(false));
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') setOpen(false);
  });

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const message = input.value.trim();
    if (!message) return;

    addMessage(message, 'user');
    input.value = '';
    sendButton.disabled = true;
    const pending = addMessage('Thinking…', 'assistant pending');

    try {
      const token = window.CampusFlow?.token || localStorage.getItem('campusflow_token');
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {})
        },
        body: JSON.stringify({ message })
      });

      // The server may return non-JSON (e.g. an HTML error page).
      let result = {};
      try {
        result = await response.json();
      } catch (_) {
        /* ignore parse errors; handled below */
      }

      if (response.status === 401) {
        throw new Error('Please log in to use Campus AI.');
      }
      if (!response.ok || !result.success) {
        throw new Error(result.message || 'Unable to contact Campus AI.');
      }

      pending.textContent = result.answer || 'No answer received.';
    } catch (error) {
      pending.textContent = error.message || 'Could not reach the server.';
      pending.classList.add('error');
    } finally {
      pending.classList.remove('pending');
      sendButton.disabled = false;
      messages.scrollTop = messages.scrollHeight;
      input.focus();
    }
  });
})();