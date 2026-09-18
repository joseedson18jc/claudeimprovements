document.addEventListener('DOMContentLoaded', () => {

  // --- Card selection ---
  const cards = document.querySelectorAll('.screen-card');
  const thumbs = document.querySelectorAll('.sidebar-thumb');

  function selectCard(index) {
    cards.forEach((c, i) => {
      c.classList.toggle('selected', i === index);
    });
    thumbs.forEach((t, i) => {
      t.classList.toggle('thumb-active', i === index);
    });
  }

  cards.forEach((card, i) => {
    card.addEventListener('click', () => selectCard(i));
  });
  thumbs.forEach((thumb, i) => {
    thumb.addEventListener('click', () => {
      selectCard(i);
      cards[i].scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });
    });
  });

  // --- Agent log sequential reveal ---
  const logEntries = document.querySelectorAll('.agent-log-entry');
  logEntries.forEach((entry, i) => {
    entry.style.animationDelay = `${0.6 + i * 0.6}s`;
  });

  // --- Prompt bar ---
  const promptInput = document.getElementById('prompt-input');
  const sendBtn = document.getElementById('send-btn');
  const chips = document.querySelectorAll('.suggestion-chip');
  const agentLog = document.getElementById('agent-log-content');

  chips.forEach(chip => {
    chip.addEventListener('click', () => {
      promptInput.value = chip.textContent.trim();
      promptInput.focus();
    });
  });

  function handleSend() {
    const text = promptInput.value.trim();
    if (!text) return;

    const entry = document.createElement('div');
    entry.className = 'agent-log-entry animate-fade-in-up flex items-start gap-2 text-xs';
    entry.innerHTML = `
      <span class="material-symbols-outlined text-sm text-blue-400 mt-0.5" style="font-size:14px">pending</span>
      <div>
        <span class="text-gray-400">${new Date().toLocaleTimeString([], {hour:'2-digit',minute:'2-digit',second:'2-digit'})}</span>
        <span class="text-gray-300 ml-1">${escapeHtml(text)}</span>
        <span class="ml-1"><span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span></span>
      </div>
    `;
    agentLog.appendChild(entry);
    agentLog.scrollTop = agentLog.scrollHeight;
    promptInput.value = '';
  }

  function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  sendBtn.addEventListener('click', handleSend);
  promptInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  });

  // --- Sidebar toggle ---
  const sidebar = document.getElementById('sidebar');
  const sidebarToggle = document.getElementById('sidebar-toggle');
  let sidebarExpanded = true;

  sidebarToggle.addEventListener('click', () => {
    sidebarExpanded = !sidebarExpanded;
    if (sidebarExpanded) {
      sidebar.classList.remove('sidebar-collapsed');
      sidebar.classList.add('sidebar-expanded');
      sidebar.style.width = '240px';
    } else {
      sidebar.classList.remove('sidebar-expanded');
      sidebar.classList.add('sidebar-collapsed');
      sidebar.style.width = '64px';
    }
  });

  // --- Zoom controls ---
  const zoomLevels = [50, 75, 100, 125, 150];
  let currentZoomIndex = 2;
  const zoomLabel = document.getElementById('zoom-label');
  const canvasInner = document.getElementById('canvas-inner');
  const zoomIn = document.getElementById('zoom-in');
  const zoomOut = document.getElementById('zoom-out');

  function applyZoom() {
    const scale = zoomLevels[currentZoomIndex] / 100;
    canvasInner.style.transform = `scale(${scale})`;
    zoomLabel.textContent = `${zoomLevels[currentZoomIndex]}%`;
  }

  zoomIn.addEventListener('click', () => {
    if (currentZoomIndex < zoomLevels.length - 1) {
      currentZoomIndex++;
      applyZoom();
    }
  });
  zoomOut.addEventListener('click', () => {
    if (currentZoomIndex > 0) {
      currentZoomIndex--;
      applyZoom();
    }
  });

  // --- Mode toggle ---
  const modeStandard = document.getElementById('mode-standard');
  const modeExperimental = document.getElementById('mode-experimental');
  const modeIndicator = document.getElementById('mode-indicator');

  modeStandard.addEventListener('click', () => {
    modeIndicator.style.transform = 'translateX(0)';
    modeStandard.classList.add('text-white');
    modeStandard.classList.remove('text-gray-400');
    modeExperimental.classList.add('text-gray-400');
    modeExperimental.classList.remove('text-white');
  });
  modeExperimental.addEventListener('click', () => {
    modeIndicator.style.transform = 'translateX(100%)';
    modeExperimental.classList.add('text-white');
    modeExperimental.classList.remove('text-gray-400');
    modeStandard.classList.add('text-gray-400');
    modeStandard.classList.remove('text-white');
  });

  // --- Reference dock ---
  const refThumbs = document.querySelectorAll('.ref-thumb');
  refThumbs.forEach((thumb, i) => {
    thumb.addEventListener('click', () => {
      refThumbs.forEach(t => t.classList.remove('thumb-active'));
      thumb.classList.add('thumb-active');
    });
  });

  // Select first card by default
  selectCard(0);
});
