
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
window.openExercises = openExercises;

// Al final de exam.js
window.openExam = openExam;
window.submitExam = submitExam;
window.closeActivityModal = closeActivityModal;