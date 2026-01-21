// Sidebar toggle
function toggleSidebar() {
  document.body.classList.toggle('sidebar-collapsed');
}

// Accordion exclusivo na sidebar
window.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('.sidebar-group-toggle').forEach(function(toggle) {
    toggle.addEventListener('click', function(e) {
      const parent = this.parentElement;
      document.querySelectorAll('.sidebar-group.open').forEach(function(g) {
        if (g !== parent) g.classList.remove('open');
      });
      parent.classList.toggle('open');
      e.preventDefault();
    });
  });
});

// Toasts
function showToast(message, type = 'info') {
  const toast = document.createElement('div');
  toast.className = 'toast ' + type;
  toast.innerText = message;
  document.getElementById('toast-container').appendChild(toast);
  setTimeout(() => { toast.classList.add('fade'); }, 10);
  setTimeout(() => { toast.remove(); }, 3000);
}

// Show all Flask flashes as toasts
window.addEventListener('DOMContentLoaded', function() {
  const flashes = document.querySelectorAll('.flash');
  flashes.forEach(f => {
    showToast(f.innerText);
    f.remove();
  });

  // Dark mode: inicialização
  if (localStorage.getItem('darkMode') === 'true') {
    document.body.classList.add('dark-mode');
    setDarkModeIcon(true);
  } else {
    setDarkModeIcon(false);
  }
});

// Table filter
function filterTable(inputId, tableId) {
  const input = document.getElementById(inputId);
  const filter = input.value.toLowerCase();
  const table = document.getElementById(tableId);
  const trs = table.getElementsByTagName('tr');
  for (let i = 1; i < trs.length; i++) {
    let show = false;
    trs[i].querySelectorAll('td').forEach(td => {
      if (td.innerText.toLowerCase().indexOf(filter) > -1) show = true;
    });
    trs[i].style.display = show ? '' : 'none';
  }
}

// Dark mode toggle
function toggleDarkMode() {
  const isDark = document.body.classList.toggle('dark-mode');
  localStorage.setItem('darkMode', isDark);
  setDarkModeIcon(isDark);
}
function setDarkModeIcon(isDark) {
  const icon = document.getElementById('darkmode-icon');
  if (icon) {
    icon.className = isDark ? 'fa fa-sun' : 'fa fa-moon';
  }
}
