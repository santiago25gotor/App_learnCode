

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
window.openExercises = openExercises;
window.openExam = openExam;
window.submitExam = submitExam;
window.closeActivityModal = closeActivityModal;