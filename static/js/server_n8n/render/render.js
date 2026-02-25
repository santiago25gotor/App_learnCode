import { DOM } from '../DOM/dom.js';
import { escapeHtml } from '../utils/utils.js';

function renderLoadingState(message) {
    return `<div class="loading-state"><div class="loading-spinner"></div><p>${message}</p></div>`;
}

function renderErrorState(message) {
    return `
        <div class="error-state">
            <p>${message}</p>
            <button onclick="window.eduAI.loadVideos()" class="quick-tag">Reintentar</button>
        </div>`;
}

function createVideoCard(video, index) {
    const title = escapeHtml(video.video_title || 'Sin título');
    const teoria = escapeHtml(video.teoria || 'Sin resumen disponible');
    return `
        <article class="video-card">
            <div class="video-body">
                <h3>${title}</h3>
                <div class="video-description">${teoria}</div>
            </div>
            <div class="video-footer">
                <button class="watch-btn" onclick="window.openCourseModal(${index})">Acceder al curso</button>
            </div>
        </article>`;
}

export function showLoading(message) { DOM.videosContainer.innerHTML = renderLoadingState(message); }
export function showError(message) { DOM.videosContainer.innerHTML = renderErrorState(message); }
export function displayVideos(videos) {
    if (!videos || videos.length === 0) {
        DOM.videosContainer.innerHTML = '<p>No se encontraron videos.</p>';
        return;
    }
    DOM.videosContainer.innerHTML = videos.map((v, i) => createVideoCard(v, i)).join('');
}