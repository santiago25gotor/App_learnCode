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
            const activeTab = document.getElementById('tabSyllabus').classList.contains('bg-primary') ? 'syllabus' : 'path';
            
            if (activeTab === 'syllabus') {
                renderSyllabusSearch(results);
            } else {
                renderPathSearch(results);
            }

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
    const activeTab = document.getElementById('tabSyllabus').classList.contains('bg-primary') ? 'syllabus' : 'path';
    
    if (activeTab === 'syllabus') {
        renderSyllabus();
    } else {
        renderLearningPath();
    }
}

// Renderizar resultados en vista Temario
function renderSyllabusSearch(results) {
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
            const isCompleted = completedLessons.includes(lesson.id);
            
            // 🆕 NUEVO: Verificar si está bloqueada
            const isLocked = index > 0 && !completedLessons.includes(lessons[index - 1]?.id);
            
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
// Renderizar resultados en vista Ruta de Aprendizaje
function renderPathSearch(results) {
    const container = document.getElementById('lessonsPath');
    
    if (results.length === 0) {
        container.innerHTML = `
            <div class="flex flex-col items-center justify-center py-20 text-center">
                <span class="material-symbols-outlined text-6xl text-gray-300 dark:text-gray-700 mb-4">search_off</span>
                <h3 class="text-2xl font-bold text-gray-600 dark:text-gray-400 mb-2">No se encontraron resultados</h3>
                <p class="text-gray-500 dark:text-gray-500 max-w-md">
                    Intenta con otros términos de búsqueda o limpia los filtros
                </p>
            </div>
        `;
        return;
    }

    const completed = userProgress.completed_lessons || [];
    let html = '';

    results.forEach((lesson, index) => {
        const isCompleted = completed.includes(lesson.id);
        const alignment = index % 2 === 0 ? 'md:justify-end md:pr-12' : 'md:justify-start md:pl-12';

        html += `
            <div class="flex ${alignment} pl-16 md:pl-0 relative w-full">
                <div class="absolute left-6 md:hidden w-5 h-5 -ml-0.5 rounded-full ${isCompleted ? 'bg-green-500' : 'bg-primary'} border-2 border-white dark:border-gray-900 top-1/2 -translate-y-1/2 z-10"></div>
                <div class="w-full md:w-80 bg-white dark:bg-gray-900 p-6 rounded-xl shadow-xl border-2 ${isCompleted ? 'border-green-500' : 'border-primary'} hover:-translate-y-1 transition-transform duration-300 cursor-pointer" onclick="startLesson('${lesson.id}')">
                    ${isCompleted ? 
                        '<div class="absolute -right-2 -top-2 bg-green-500 text-white rounded-full p-1 shadow-sm"><span class="material-icons text-sm">check</span></div>' : 
                        '<div class="absolute -right-2 -top-2 bg-primary text-black rounded-full p-2 shadow-lg"><span class="material-icons text-sm">search</span></div>'
                    }
                    <div class="flex justify-between items-start mb-3">
                        <span class="bg-primary text-black text-xs font-bold px-2 py-1 rounded uppercase">Resultado</span>
                        <span class="text-xs font-mono text-gray-500">#${lesson.numero_leccion}</span>
                    </div>
                    <h3 class="text-xl font-bold mb-2">${highlightMatch(lesson.titulo, currentSearchQuery)}</h3>
                    <p class="text-gray-600 dark:text-gray-300 text-sm mb-4">${highlightMatch(lesson.descripcion?.substring(0, 100) || '', currentSearchQuery)}...</p>
                    <div class="flex items-center justify-between">
                        <span class="text-xs font-bold px-3 py-1 rounded-full ${isCompleted ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400' : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400'}">
                            ${lesson.categoria}
                        </span>
                        <span class="text-xs font-mono ${isCompleted ? 'text-green-600' : 'text-gray-600'} bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">
                            ${isCompleted ? '✓ 10 XP' : '10 XP'}
                        </span>
                    </div>
                </div>
            </div>
        `;
    });

    container.innerHTML = html;
}

// Resaltar coincidencias en el texto
function highlightMatch(text, query) {
    if (!text || !query) return text || '';
    
    const regex = new RegExp(`(${query})`, 'gi');
    return text.replace(regex, '<mark class="bg-primary/40 dark:bg-primary/20 px-1 rounded">$1</mark>');
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