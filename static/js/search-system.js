// ============================================
// SISTEMA DE BÚSQUEDA - PYLEARN
// ============================================

let currentSearchQuery = '';
let isSearchActive = false;

// Realizar búsqueda
async function performSearch() {
    const query = document.getElementById('searchInput').value.trim();
    
    if (!query) {
        clearSearch();
        return;
    }

    currentSearchQuery = query;
    isSearchActive = true;

    // Mostrar indicadores
    document.getElementById('searchQuery').textContent = query;
    document.getElementById('searchIndicator').classList.remove('hidden');
    document.getElementById('clearSearchBtn').classList.remove('hidden');

    try {
        const response = await fetch(`/api/lessons/search?q=${encodeURIComponent(query)}`);
        const data = await response.json();

        if (data.success) {
            const results = data.results;
            
            // Mostrar cantidad de resultados
            document.getElementById('searchResultsText').textContent = 
                `Se encontraron ${results.length} lección${results.length !== 1 ? 'es' : ''} que coinciden con tu búsqueda`;
            document.getElementById('searchResults').classList.remove('hidden');
            document.getElementById('noResults').classList.add('hidden');

            // Renderizar según la pestaña activa
            renderSyllabusSearch(results);

            // Si no hay resultados
            if (results.length === 0) {
                document.getElementById('searchResults').classList.add('hidden');
                document.getElementById('noResults').classList.remove('hidden');
            }

        } else {
            console.error('Error en búsqueda:', data.message);
            showSearchError();
        }
    } catch (error) {
        console.error('Error al buscar:', error);
        showSearchError();
    }
}

// Limpiar búsqueda
function clearSearch() {
    currentSearchQuery = '';
    isSearchActive = false;
    
    document.getElementById('searchInput').value = '';
    document.getElementById('searchIndicator').classList.add('hidden');
    document.getElementById('searchResults').classList.add('hidden');
    document.getElementById('noResults').classList.add('hidden');
    document.getElementById('clearSearchBtn').classList.add('hidden');

    // Restaurar vista normal
    renderSyllabus();
}

// Renderizar resultados en vista Temario
function renderSyllabusSearch(results) {
    // Obtener lecciones completadas desde el contexto global de course_new.html
    const completed = window.completedLessons || [];
    
    const categories = {
        'Python Básico': { id: 'basicLessonsList', lessons: [] },
        'Python Intermedio': { id: 'intermediateLessonsList', lessons: [] },
        'Python Avanzado': { id: 'advancedLessonsList', lessons: [] }
    };

    results.forEach(lesson => {
        const cat = lesson.categoria || 'Python Básico';
        if (categories[cat]) {
            categories[cat].lessons.push(lesson);
        }
    });

    Object.entries(categories).forEach(([catName, catData]) => {
        const container = document.getElementById(catData.id);
        if (!container) return;

        const lessons = catData.lessons;

        if (lessons.length === 0) {
            container.innerHTML = `
                <div class="text-center text-gray-400 py-6 text-sm">
                    <span class="material-symbols-outlined text-3xl mb-2 opacity-50">search_off</span>
                    <p>No se encontraron resultados en esta categoría</p>
                </div>
            `;
            return;
        }

        container.innerHTML = lessons.map((lesson, index) => {
            const isCompleted = completed.includes(lesson.id);
            
            // Verificar si está bloqueada (buscar en todas las lecciones, no solo en results)
            const allLessons = window.allLessons || [];
            const lessonGlobalIndex = allLessons.findIndex(l => l.id === lesson.id);
            const isLocked = lessonGlobalIndex > 0 && !completed.includes(allLessons[lessonGlobalIndex - 1]?.id);
            
            return `
                <div class="flex items-center gap-3 p-3 rounded-lg bg-yellow-50 dark:bg-yellow-900/10 border border-yellow-200 dark:border-yellow-800 hover:bg-yellow-100 dark:hover:bg-yellow-900/20 cursor-pointer transition-colors"
                     onclick="startLesson('${lesson.id}')">
                    <div class="flex-shrink-0">
                        ${isCompleted ?
                            '<span class="material-symbols-outlined text-green-600 dark:text-green-400">check_circle</span>' :
                            isLocked ?
                            '<span class="material-symbols-outlined text-orange-500">visibility</span>' :
                            '<span class="material-symbols-outlined text-primary">search</span>'
                        }
                    </div>
                    <div class="flex-1 min-w-0">
                        <div class="font-bold text-gray-900 dark:text-white truncate">
                            ${highlightMatch(lesson.titulo, currentSearchQuery)}
                            ${isLocked ? '<span class="ml-2 text-xs bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-400 px-2 py-0.5 rounded">Vista Previa</span>' : ''}
                        </div>
                        ${lesson.descripcion ? `<div class="text-xs text-gray-600 dark:text-gray-400 truncate">${highlightMatch(lesson.descripcion.substring(0, 80), currentSearchQuery)}...</div>` : ''}
                    </div>
                    <div class="flex items-center gap-2 text-xs">
                        <span class="bg-primary/20 text-black dark:text-primary px-2 py-1 rounded font-bold">
                            ${isCompleted ? '✓ +10 XP' : isLocked ? '👁️ Solo lectura' : '10 XP'}
                        </span>
                    </div>
                </div>
            `;
        }).join('');
    });
}

// Resaltar coincidencias en el texto
function highlightMatch(text, query) {
    if (!text || !query) return text || '';
    
    const regex = new RegExp(`(${escapeRegex(query)})`, 'gi');
    return text.replace(regex, '<mark class="bg-primary/40 dark:bg-primary/20 px-1 rounded">$1</mark>');
}

// Escapar caracteres especiales en regex
function escapeRegex(str) {
    return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

// Mostrar error en búsqueda
function showSearchError() {
    document.getElementById('searchResults').classList.add('hidden');
    document.getElementById('noResults').classList.remove('hidden');
}

// Inicializar event listeners
document.addEventListener('DOMContentLoaded', function() {
    const searchBtn = document.getElementById('searchBtn');
    const searchInput = document.getElementById('searchInput');

    if (searchBtn) {
        searchBtn.addEventListener('click', performSearch);
    }

    if (searchInput) {
        searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                performSearch();
            }
        });

        searchInput.addEventListener('input', (e) => {
            const clearBtn = document.getElementById('clearSearchBtn');
            if (e.target.value.trim()) {
                clearBtn.classList.remove('hidden');
            } else {
                clearBtn.classList.add('hidden');
            }
        });
    }
});