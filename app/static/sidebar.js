// Sidebar toggle
function toggleSidebar() {
  document.body.classList.toggle('sidebar-collapsed');
}

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
