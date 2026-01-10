// main.js - Frontend improvements for eskola app

// Responsive Navigation Menu
document.addEventListener('DOMContentLoaded', function() {
    const hamburger = document.querySelector('.hamburger');
    const menuDropdown = document.querySelector('.menu-dropdown');

    if (hamburger && menuDropdown) {
        hamburger.addEventListener('click', function() {
            menuDropdown.classList.toggle('open');
        });

        // Close menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!hamburger.contains(e.target) && !menuDropdown.contains(e.target)) {
                menuDropdown.classList.remove('open');
            }
        });

        // Close menu when clicking on a link
        menuDropdown.addEventListener('click', function(e) {
            if (e.target.tagName === 'A') {
                menuDropdown.classList.remove('open');
            }
        });
    }
});

// Client-Side Form Validation
function validateForm(form) {
    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    let isValid = true;

    inputs.forEach(input => {
        if (!input.value.trim()) {
            showError(input, 'Este campo é obrigatório');
            isValid = false;
        } else {
            clearError(input);
            // Additional validations
            if (input.type === 'email' && !isValidEmail(input.value)) {
                showError(input, 'Email inválido');
                isValid = false;
            }
            if (input.type === 'password' && input.value.length < 6) {
                showError(input, 'A senha deve ter pelo menos 6 caracteres');
                isValid = false;
            }
        }
    });

    return isValid;
}

function showError(input, message) {
    clearError(input);
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    input.parentNode.insertBefore(errorDiv, input.nextSibling);
    input.classList.add('error');
}

function clearError(input) {
    const errorDiv = input.parentNode.querySelector('.error-message');
    if (errorDiv) {
        errorDiv.remove();
    }
    input.classList.remove('error');
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Attach validation to all forms
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(form)) {
                e.preventDefault();
            }
        });

        // Real-time validation
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                if (input.hasAttribute('required') && !input.value.trim()) {
                    showError(input, 'Este campo é obrigatório');
                } else {
                    clearError(input);
                    if (input.type === 'email' && input.value && !isValidEmail(input.value)) {
                        showError(input, 'Email inválido');
                    }
                    if (input.type === 'password' && input.value && input.value.length < 6) {
                        showError(input, 'A senha deve ter pelo menos 6 caracteres');
                    }
                }
            });
        });
    });

    // Handle delete forms with custom modal
    const deleteForms = document.querySelectorAll('.delete-form');
    deleteForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            showConfirmModal('Tem certeza que deseja deletar este item?', (confirmed) => {
                if (confirmed) {
                    form.submit();
                }
            });
        });
    });
});

// Custom Confirmation Modals
function showConfirmModal(message, callback) {
    // Create modal elements
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal">
            <p>${message}</p>
            <div class="modal-buttons">
                <button class="btn-confirm">Confirmar</button>
                <button class="btn-cancel">Cancelar</button>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    const confirmBtn = modal.querySelector('.btn-confirm');
    const cancelBtn = modal.querySelector('.btn-cancel');

    confirmBtn.addEventListener('click', function() {
        document.body.removeChild(modal);
        callback(true);
    });

    cancelBtn.addEventListener('click', function() {
        document.body.removeChild(modal);
        callback(false);
    });

    // Close on overlay click
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            document.body.removeChild(modal);
            callback(false);
        }
    });
}

// Flash Message Enhancements
document.addEventListener('DOMContentLoaded', function() {
    const flashes = document.querySelectorAll('.flash');
    flashes.forEach(flash => {
        // Add close button
        const closeBtn = document.createElement('button');
        closeBtn.className = 'flash-close';
        closeBtn.innerHTML = '&times;';
        closeBtn.setAttribute('aria-label', 'Fechar mensagem');
        flash.appendChild(closeBtn);

        closeBtn.addEventListener('click', function() {
            flash.style.opacity = '0';
            setTimeout(() => flash.remove(), 300);
        });

        // Auto-hide after 5 seconds
        setTimeout(() => {
            if (flash.parentNode) {
                flash.style.opacity = '0';
                setTimeout(() => flash.remove(), 300);
            }
        }, 5000);
    });
});

// Loading Indicators
function showLoading(element) {
    const loader = document.createElement('div');
    loader.className = 'loading-indicator';
    loader.innerHTML = '<div class="spinner"></div>';
    element.appendChild(loader);
    return loader;
}

function hideLoading(loader) {
    if (loader && loader.parentNode) {
        loader.parentNode.removeChild(loader);
    }
}

// AJAX Helper
function ajaxRequest(url, options = {}) {
    return fetch(url, {
        method: options.method || 'GET',
        headers: {
            'Content-Type': 'application/json',
            ...options.headers
        },
        body: options.body ? JSON.stringify(options.body) : undefined
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    });
}

// Dynamic Content Loading for Announcements
document.addEventListener('DOMContentLoaded', function() {
    const anunciosContainer = document.querySelector('.anuncios-container');
    if (anunciosContainer) {
        loadAnnouncements(anunciosContainer);
    }
});

function loadAnnouncements(container, page = 1, search = '') {
    const loader = showLoading(container);

    ajaxRequest(`/api/anuncios?page=${page}&search=${encodeURIComponent(search)}`)
        .then(data => {
            hideLoading(loader);
            renderAnnouncements(container, data.anuncios);
            updatePagination(data.hasMore, page);
        })
        .catch(error => {
            hideLoading(loader);
            console.error('Error loading announcements:', error);
            container.innerHTML = '<p>Erro ao carregar anúncios.</p>';
        });
}

function renderAnnouncements(container, anuncios) {
    const html = anuncios.map(anuncio => `
        <div class="anuncio">
            <h3>${anuncio.titulo}</h3>
            <p>${anuncio.conteudo}</p>
            <small>Publicado em ${anuncio.data_publicacao}</small>
        </div>
    `).join('');
    container.innerHTML = html;
}

function updatePagination(hasMore, currentPage) {
    // Implement pagination if needed
}

// Search and Filter Functionality
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.querySelector('#search-anuncios');
    if (searchInput) {
        let timeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                const container = document.querySelector('.anuncios-container');
                if (container) {
                    loadAnnouncements(container, 1, this.value);
                }
            }, 300);
        });
    }
});