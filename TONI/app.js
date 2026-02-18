// ============================================
// CONFIGURATION
// ============================================
const CONFIG = {
    WEBHOOK_URL: 'https://toni2005cm.app.n8n.cloud/webhook/youtube-education',
    AUTO_LOAD_ON_START: true
};

// ============================================
// DOM ELEMENTS
// ============================================
const DOM = {
    videosContainer: document.getElementById('videos-container'),
    searchInput: document.getElementById('search-input'),
    searchButton: document.getElementById('search-button'),
    quickTags: document.querySelectorAll('.quick-tag'),
    viewControls: document.querySelectorAll('.control-btn')
};

// ============================================
// STATE
// ============================================
const state = {
    isLoading: false,
    currentVideos: []
};

// ============================================
// UI COMPONENTS
// ============================================

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
                <button class="watch-btn" onclick="openCourseModal(${index})">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M22 10v6M2 10l10-5 10 5-10 5z"></path>
                        <path d="M6 12v5c3 3 9 3 12 0v-5"></path>
                    </svg>
                    Acceder al curso
                </button>
            </div>
        </article>
    `;
}

// ============================================
// API FUNCTIONS
// ============================================

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

// ============================================
// UI UPDATE FUNCTIONS
// ============================================

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

// ============================================
// UTILITY FUNCTIONS
// ============================================

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

// ============================================
// EVENT LISTENERS
// ============================================

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

// ============================================
// INITIALIZATION
// ============================================

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

// ============================================
// COURSE MODAL
// ============================================

function openCourseModal(index) {
    const video = state.currentVideos[index];
    if (!video) return;

    const videoId = video.video_id || '';
    const title = video.video_title || 'Video sin título';
    const teoria = video.teoria || 'Sin contenido disponible.';

    // Parse questions safely
    let preguntas_test = [];
    let preguntas_examen = [];
    try { preguntas_test = typeof video.preguntas_test === 'string' ? JSON.parse(video.preguntas_test) : (video.preguntas_test || []); } catch(e) {}
    try { preguntas_examen = typeof video.preguntas_examen === 'string' ? JSON.parse(video.preguntas_examen) : (video.preguntas_examen || []); } catch(e) {}

    const modal = document.createElement('div');
    modal.id = 'course-modal';
    modal.className = 'course-modal-overlay';
    modal.innerHTML = `
        <div class="course-modal">
            <div class="course-modal-header">
                <h2 class="course-modal-title">${escapeHtml(title)}</h2>
                <button class="course-modal-close" onclick="closeCourseModal()" title="Cerrar">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                </button>
            </div>

            <div class="course-modal-body">
                <!-- Left: Video -->
                <div class="course-video-panel">
                    <div class="course-video-wrapper">
                        <iframe
                            src="https://www.youtube.com/embed/${escapeHtml(videoId)}?rel=0&modestbranding=1"
                            title="${escapeHtml(title)}"
                            frameborder="0"
                            allowfullscreen
                            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture">
                        </iframe>
                    </div>
                    <div class="course-video-label">
                        <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16">
                            <polygon points="5 3 19 12 5 21 5 3"></polygon>
                        </svg>
                        Video del curso
                    </div>
                </div>

                <!-- Right: Theory -->
                <div class="course-theory-panel">
                    <div class="course-theory-header">
                        <span class="ai-badge">🤖 Resumen IA</span>
                        <h3>Teoría del curso</h3>
                    </div>
                    <div class="course-theory-content">
                        <p>${escapeHtml(teoria)}</p>
                    </div>
                </div>
            </div>

            <!-- Bottom action buttons -->
            <div class="course-modal-footer">
                <button class="course-action-btn btn-exercises" onclick='openExercises(${JSON.stringify(preguntas_test).replace(/'/g, "&#39;")})'>
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M9 11l3 3L22 4"></path>
                        <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path>
                    </svg>
                    Realizar Ejercicios
                </button>
                <button class="course-action-btn btn-exam" onclick='openExam(${JSON.stringify(preguntas_examen).replace(/'/g, "&#39;")})'>
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                        <polyline points="14 2 14 8 20 8"></polyline>
                        <line x1="16" y1="13" x2="8" y2="13"></line>
                        <line x1="16" y1="17" x2="8" y2="17"></line>
                        <polyline points="10 9 9 9 8 9"></polyline>
                    </svg>
                    Realizar Examen
                </button>
            </div>
        </div>
    `;

    document.body.appendChild(modal);
    document.body.style.overflow = 'hidden';

    // Close on overlay click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeCourseModal();
    });

    // Close on ESC
    document.addEventListener('keydown', handleModalEsc);

    requestAnimationFrame(() => modal.classList.add('visible'));
}

function closeCourseModal() {
    const modal = document.getElementById('course-modal');
    if (!modal) return;
    modal.classList.remove('visible');
    document.removeEventListener('keydown', handleModalEsc);
    setTimeout(() => {
        modal.remove();
        document.body.style.overflow = '';
    }, 350);
}

function handleModalEsc(e) {
    if (e.key === 'Escape') closeCourseModal();
}

// ============================================
// EXERCISES (Multiple Choice)
// ============================================

function openExercises(questions) {
    if (!questions || questions.length === 0) {
        showNotification('⚠️ No hay ejercicios disponibles para este video', 'warning');
        return;
    }

    let currentQ = 0;
    let score = 0;
    let answered = false;

    function renderQuestion() {
        const q = questions[currentQ];
        const letters = ['A', 'B', 'C', 'D'];
        const optionsHTML = (q.opciones || []).map((opt, i) => `
            <button class="quiz-option" data-letter="${letters[i]}" onclick="selectOption(this, '${letters[i]}', '${q.respuesta_correcta}')">
                <span class="quiz-option-letter">${letters[i]}</span>
                <span class="quiz-option-text">${escapeHtml(opt)}</span>
            </button>
        `).join('');

        return `
            <div class="quiz-progress">
                <span>Pregunta ${currentQ + 1} de ${questions.length}</span>
                <div class="quiz-progress-bar">
                    <div class="quiz-progress-fill" style="width: ${((currentQ) / questions.length) * 100}%"></div>
                </div>
                <span>Puntuación: ${score}/${currentQ}</span>
            </div>
            <div class="quiz-question">
                <p>${escapeHtml(q.pregunta)}</p>
            </div>
            <div class="quiz-options" id="quiz-options">
                ${optionsHTML}
            </div>
            <div class="quiz-nav">
                <button class="quiz-next-btn" id="quiz-next" style="display:none" onclick="nextQuestion()">
                    ${currentQ < questions.length - 1 ? 'Siguiente pregunta →' : 'Ver resultado'}
                </button>
            </div>
        `;
    }

    function renderResult() {
        const pct = Math.round((score / questions.length) * 100);
        const emoji = pct >= 80 ? '🎉' : pct >= 50 ? '👍' : '📚';
        return `
            <div class="quiz-result">
                <div class="quiz-result-emoji">${emoji}</div>
                <h3>¡Ejercicios completados!</h3>
                <div class="quiz-result-score">${score} / ${questions.length}</div>
                <p class="quiz-result-pct">${pct}% de aciertos</p>
                <p class="quiz-result-msg">${pct >= 80 ? 'Excelente trabajo. ¡Dominas el tema!' : pct >= 50 ? 'Buen trabajo. ¡Sigue practicando!' : 'Repasa el material y vuelve a intentarlo.'}</p>
                <button class="course-action-btn btn-exercises" onclick="closeActivityModal()" style="margin-top:1.5rem; display:inline-flex;">
                    Volver al curso
                </button>
            </div>
        `;
    }

    openActivityModal('📝 Ejercicios de práctica', renderQuestion());

    // Expose helpers to window for onclick handlers
    window.selectOption = function(btn, letter, correct) {
        if (answered) return;
        answered = true;
        const allBtns = document.querySelectorAll('.quiz-option');
        allBtns.forEach(b => {
            b.disabled = true;
            if (b.dataset.letter === correct) b.classList.add('correct');
        });
        if (letter === correct) {
            btn.classList.add('correct');
            score++;
        } else {
            btn.classList.add('wrong');
        }
        document.getElementById('quiz-next').style.display = 'inline-flex';
    };

    window.nextQuestion = function() {
        currentQ++;
        answered = false;
        const body = document.getElementById('activity-body');
        if (currentQ >= questions.length) {
            body.innerHTML = renderResult();
        } else {
            body.innerHTML = renderQuestion();
        }
    };
}

// ============================================
// EXAM (Open-ended)
// ============================================

function openExam(questions) {
    if (!questions || questions.length === 0) {
        showNotification('⚠️ No hay preguntas de examen disponibles', 'warning');
        return;
    }

    const questionsHTML = questions.map((q, i) => `
        <div class="exam-question">
            <label class="exam-question-label">
                <span class="exam-q-num">${i + 1}</span>
                ${escapeHtml(q.pregunta)}
            </label>
            <textarea class="exam-textarea" id="exam-answer-${i}" placeholder="Escribe tu respuesta aquí..."></textarea>
        </div>
    `).join('');

    const html = `
        <p class="exam-intro">Responde las siguientes preguntas con tus propias palabras. Después podrás comparar con los puntos clave.</p>
        <div class="exam-questions">${questionsHTML}</div>
        <button class="course-action-btn btn-exam" onclick="submitExam()" style="margin-top:1.5rem; width:100%; justify-content:center;">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
                <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
            Entregar examen
        </button>
    `;

    openActivityModal('📄 Examen del curso', html);

    window.submitExam = function() {
        const resultsHTML = questions.map((q, i) => {
            const answer = (document.getElementById(`exam-answer-${i}`)?.value || '').trim();
            const keyPoints = (q.puntos_clave || []).map(pk => `<li>${escapeHtml(pk)}</li>`).join('');
            return `
                <div class="exam-result-item">
                    <div class="exam-result-question">
                        <span class="exam-q-num">${i + 1}</span>
                        ${escapeHtml(q.pregunta)}
                    </div>
                    <div class="exam-result-answer">
                        <strong>Tu respuesta:</strong>
                        <p>${answer ? escapeHtml(answer) : '<em>Sin respuesta</em>'}</p>
                    </div>
                    <div class="exam-result-keys">
                        <strong>✅ Puntos clave esperados:</strong>
                        <ul>${keyPoints}</ul>
                    </div>
                </div>
            `;
        }).join('');

        const body = document.getElementById('activity-body');
        body.innerHTML = `
            <div class="exam-results">
                <div class="exam-results-header">
                    <span style="font-size:2.5rem">📋</span>
                    <h3>Resultados del examen</h3>
                    <p>Compara tus respuestas con los puntos clave</p>
                </div>
                ${resultsHTML}
                <button class="course-action-btn btn-exercises" onclick="closeActivityModal()" style="margin-top:1.5rem; width:100%; justify-content:center;">
                    Volver al curso
                </button>
            </div>
        `;
    };
}

// ============================================
// ACTIVITY MODAL (shared for exercises & exam)
// ============================================

function openActivityModal(title, bodyHTML) {
    // Close existing activity modal if any
    closeActivityModal();

    const modal = document.createElement('div');
    modal.id = 'activity-modal';
    modal.className = 'course-modal-overlay activity-overlay';
    modal.innerHTML = `
        <div class="course-modal activity-modal">
            <div class="course-modal-header">
                <h2 class="course-modal-title">${title}</h2>
                <button class="course-modal-close" onclick="closeActivityModal()" title="Cerrar">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                </button>
            </div>
            <div class="activity-modal-body" id="activity-body">
                ${bodyHTML}
            </div>
        </div>
    `;

    document.body.appendChild(modal);
    modal.addEventListener('click', (e) => { if (e.target === modal) closeActivityModal(); });
    requestAnimationFrame(() => modal.classList.add('visible'));
}

function closeActivityModal() {
    const modal = document.getElementById('activity-modal');
    if (!modal) return;
    modal.classList.remove('visible');
    setTimeout(() => modal.remove(), 350);
}

// Export for debugging
window.eduAI = {
    loadVideos,
    searchVideo,
    state,
    config: CONFIG
};