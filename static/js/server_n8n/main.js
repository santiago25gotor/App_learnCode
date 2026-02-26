import { state } from './estado_global/state.js';
import { CONFIG } from './configuration/config.js';
import { DOM, setSearchButtonLoading } from './DOM/dom.js';
import { getVideosRequest, searchVideoRequest } from './api/videosApi.js';
import { displayVideos, showLoading, showError } from './render/render.js';
import { showNotification } from './notificaciones/notificaciones.js';

async function loadVideos() {
    if (state.isLoading) return;
    state.isLoading = true;
    showLoading('Cargando biblioteca...');
    try {
        const data = await getVideosRequest();
        state.currentVideos = Array.isArray(data) ? data : [data];
        displayVideos(state.currentVideos);
    } catch (error) {
        showError("Error al conectar con el servidor.");
    } finally {
        state.isLoading = false;
    }
}

async function searchVideo(query) {
    if (!query) return;
    state.isLoading = true;
    setSearchButtonLoading(true);
    try {
        await searchVideoRequest(query);
        showNotification('Video procesado con éxito', 'success');
        await loadVideos();
    } catch (error) {
        showNotification('Error al procesar el video', 'error');
    } finally {
        state.isLoading = false;
        setSearchButtonLoading(false);
    }
}

function init() {
    DOM.searchButton.addEventListener('click', () => searchVideo(DOM.searchInput.value));
    if (CONFIG.AUTO_LOAD_ON_START) loadVideos();
}

document.addEventListener('DOMContentLoaded', init);

// Exponemos loadVideos para que el botón "Reintentar" del error funcione
window.eduAI = { loadVideos };