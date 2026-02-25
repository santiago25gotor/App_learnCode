
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

window.openCourseModal = openCourseModal;
window.closeCourseModal = closeCourseModal;