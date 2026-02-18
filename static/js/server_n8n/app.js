const CONFIG = {
    WEBHOOK_URL: 'https://toni2005cm.app.n8n.cloud/webhook/youtube-education',
    AUTO_LOAD_ON_START: true
};


const DOM = {
    videosContainer: document.getElementById('videos-container'),
    searchInput: document.getElementById('search-input'),
    searchButton: document.getElementById('search-button'),
    quickTags: document.querySelectorAll('.quick-tag'),
    viewControls: document.querySelectorAll('.control-btn')
};

// STATE
const state = {
    isLoading: false,
    currentVideos: []
};

// UI COMPONENTS

function renderLoadingState(message = 'Cargando videos...') {
    return `
        <div class="loading-state">
            <div class="loading-spinner"></div>
            <p class="loading-text">${message}</p>
        </div>
    `;
}

function renderErrorState(message) {
    return `
        <div class="error-state">
            <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="color: #EF4444; margin: 0 auto 1rem;">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="15" y1="9" x2="9" y2="15"></line>
                <line x1="9" y1="9" x2="15" y2="15"></line>
            </svg>
            <p class="error-text">${message}</p>
            <button onclick="loadVideos()" class="quick-tag" style="margin-top: 1.5rem;">
                Reintentar
            </button>
        </div>
    `;
}

function renderEmptyState() {
    return `
        <div class="empty-state">
            <svg width="120" height="120" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="color: var(--text-muted); margin: 0 auto 1.5rem; opacity: 0.5;">
                <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path>
                <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path>
            </svg>
            <h3 style="font-size: 1.5rem; margin-bottom: 0.5rem;">Tu biblioteca está vacía</h3>
            <p class="empty-text">
                Busca un tema arriba para comenzar a agregar videos educativos
            </p>
        </div>
    `;
}

function createVideoCard(video, index) {
    const fecha = video.fecha_creacion 
        ? new Date(video.fecha_creacion).toLocaleDateString('es-ES', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        })
        : 'Fecha desconocida';
    
    const title = escapeHtml(video.video_title || 'Video sin título');
    const videoId = escapeHtml(video.video_id || 'N/A');
    const teoria = escapeHtml(video.teoria || 'Analizando contenido...');
    const videoUrl = escapeHtml(video.video_url || '#');

    return `
        <article class="video-card" style="animation-delay: ${index * 0.05}s">
            <div class="video-header">
                <h3 class="video-title">${title}</h3>
                <div class="video-meta">
                    <span class="meta-item">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                            <line x1="16" y1="2" x2="16" y2="6"></line>
                            <line x1="8" y1="2" x2="8" y2="6"></line>
                            <line x1="3" y1="10" x2="21" y2="10"></line>
                        </svg>
                        ${fecha}
                    </span>
                    <span class="meta-item">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                            <polyline points="14 2 14 8 20 8"></polyline>
                        </svg>
                        ${videoId}
                    </span>
                </div>
            </div>
            
            <div class="video-body">
                <span class="ai-badge">🤖 Resumen IA</span>
                <div class="video-description">${teoria}</div>
            </div>
            
            <div class="video-footer">
                <a href="${videoUrl}" target="_blank" rel="noopener noreferrer" class="watch-btn">
                    <svg viewBox="0 0 24 24" fill="currentColor">
                        <polygon points="5 3 19 12 5 21 5 3"></polygon>
                    </svg>
                    Ver en YouTube
                </a>
            </div>
        </article>
    `;
}

// API FUNCTIONS

async function loadVideos() {
    if (state.isLoading) return;
    
    state.isLoading = true;
    DOM.videosContainer.innerHTML = renderLoadingState('Cargando tu biblioteca...');

    try {
        const response = await fetch(CONFIG.WEBHOOK_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: 'getVideos' })
        });

        if (!response.ok) {
            throw new Error(`Error del servidor (${response.status})`);
        }

        const data = await response.json();
        state.currentVideos = Array.isArray(data) ? data : [data];
        
        displayVideos(state.currentVideos);

    } catch (error) {
        console.error('Error loading videos:', error);
        DOM.videosContainer.innerHTML = renderErrorState(
            `No se pudieron cargar los videos. ${error.message}`
        );
    } finally {
        state.isLoading = false;
    }
}

async function searchVideo(query) {
    if (!query || !query.trim()) {
        showNotification('⚠️ Por favor, escribe algo para buscar', 'warning');
        return;
    }

    if (state.isLoading) return;

    state.isLoading = true;
    setButtonLoading(true);
    DOM.videosContainer.innerHTML = renderLoadingState('🤖 La IA está analizando el video...');

    try {
        const response = await fetch(CONFIG.WEBHOOK_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ searchQuery: query.trim() })
        });

        if (!response.ok) {
            throw new Error(`Error del servidor (${response.status})`);
        }

        // Success
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        DOM.searchInput.value = '';
        await loadVideos();
        
        showNotification('✅ ¡Video analizado y guardado exitosamente!', 'success');

    } catch (error) {
        console.error('Error searching video:', error);
        showNotification(
            `❌ Error al buscar: ${error.message}`,
            'error'
        );
        await loadVideos();
    } finally {
        state.isLoading = false;
        setButtonLoading(false);
    }
}

// UI UPDATE FUNCTIONS

function displayVideos(videos) {
    if (!videos || videos.length === 0) {
        DOM.videosContainer.innerHTML = renderEmptyState();
        return;
    }

    const videosHTML = videos
        .map((video, index) => createVideoCard(video, index))
        .join('');

    DOM.videosContainer.innerHTML = videosHTML;
}

function setButtonLoading(isLoading) {
    const button = DOM.searchButton;
    const buttonText = button.querySelector('span');
    
    if (isLoading) {
        button.disabled = true;
        buttonText.textContent = 'Analizando...';
        button.style.opacity = '0.7';
    } else {
        button.disabled = false;
        buttonText.textContent = 'Buscar';
        button.style.opacity = '1';
    }
}

function showNotification(message, type = 'info') {
    const existing = document.querySelector('.toast-notification');
    if (existing) existing.remove();

    const colors = {
        success: 'linear-gradient(135deg, #10B981, #059669)',
        error: 'linear-gradient(135deg, #EF4444, #DC2626)',
        warning: 'linear-gradient(135deg, #F59E0B, #D97706)',
        info: 'linear-gradient(135deg, #3B82F6, #2563EB)'
    };

    const notification = document.createElement('div');
    notification.className = 'toast-notification';
    notification.textContent = message;
    
    Object.assign(notification.style, {
        position: 'fixed',
        bottom: '2rem',
        right: '2rem',
        padding: '1rem 1.5rem',
        background: colors[type] || colors.info,
        color: 'white',
        borderRadius: '12px',
        boxShadow: '0 10px 40px rgba(0, 0, 0, 0.3)',
        zIndex: '10000',
        fontWeight: '600',
        fontSize: '0.9375rem',
        animation: 'slideInRight 0.4s cubic-bezier(0.16, 1, 0.3, 1)',
        maxWidth: '400px',
        backdropFilter: 'blur(20px)'
    });

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.4s cubic-bezier(0.16, 1, 0.3, 1)';
        setTimeout(() => notification.remove(), 400);
    }, 4000);
}

// Add notification animations
const styleSheet = document.createElement('style');
styleSheet.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(styleSheet);

// UTILITY FUNCTIONS
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return String(text).replace(/[&<>"']/g, m => map[m]);
}

// EVENT LISTENERS

DOM.searchButton.addEventListener('click', () => {
    searchVideo(DOM.searchInput.value);
});

DOM.searchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        searchVideo(DOM.searchInput.value);
    }
});

DOM.quickTags.forEach(tag => {
    tag.addEventListener('click', () => {
        const query = tag.textContent.trim();
        DOM.searchInput.value = query;
        searchVideo(query);
    });
});

DOM.viewControls.forEach(btn => {
    btn.addEventListener('click', () => {
        DOM.viewControls.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        const view = btn.dataset.view;
        if (view === 'list') {
            DOM.videosContainer.style.gridTemplateColumns = '1fr';
        } else {
            DOM.videosContainer.style.gridTemplateColumns = '';
        }
    });
});

// INITIALIZATION

function init() {
    console.log('🚀 EduAI Platform inicializada');
    console.log('📡 Webhook:', CONFIG.WEBHOOK_URL);
    
    if (CONFIG.AUTO_LOAD_ON_START) {
        loadVideos();
    }
    
    DOM.searchInput.focus();
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

// Export for debugging
window.eduAI = {
    loadVideos,
    searchVideo,
    state,
    config: CONFIG
};