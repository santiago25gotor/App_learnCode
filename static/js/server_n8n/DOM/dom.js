export const DOM = {
    videosContainer: document.getElementById('videos-container'),
    searchInput: document.getElementById('search-input'),
    searchButton: document.getElementById('search-button'),
    quickTags: document.querySelectorAll('.quick-tag'),
    viewControls: document.querySelectorAll('.control-btn')
};

export function setSearchButtonLoading(isLoading) {
    const button = DOM.searchButton;
    if (!button) return;
    const buttonText = button.querySelector('span');
    
    if (isLoading) {
        button.disabled = true;
        if (buttonText) buttonText.textContent = 'Analizando...';
        button.style.opacity = '0.7';
    } else {
        button.disabled = false;
        if (buttonText) buttonText.textContent = 'Buscar';
        button.style.opacity = '1';
    }
}