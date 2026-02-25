// ── THEME ──────────────────────────────────────────────
const html = document.documentElement;
if (localStorage.getItem('theme') === 'dark') html.classList.add('dark');
function toggleDark() {
    html.classList.toggle('dark');
    localStorage.setItem('theme', html.classList.contains('dark') ? 'dark' : 'light');
    document.getElementById('themeIcon').textContent = html.classList.contains('dark') ? 'light_mode' : 'dark_mode';
}
document.getElementById('themeIcon').textContent = html.classList.contains('dark') ? 'light_mode' : 'dark_mode';

// ── TOAST ──────────────────────────────────────────────
function showToast(msg, type = 'success') {
    const t = document.getElementById('toast');
    const inner = document.getElementById('toastInner');
    const icon = document.getElementById('toastIcon');
    document.getElementById('toastMsg').textContent = msg;
    const styles = {
        success: ['bg-green-100 dark:bg-green-900/50 text-green-800 dark:text-green-200', 'check_circle'],
        error:   ['bg-red-100 dark:bg-red-900/50 text-red-800 dark:text-red-200', 'error'],
        info:    ['bg-blue-100 dark:bg-blue-900/50 text-blue-800 dark:text-blue-200', 'info'],
    };
    inner.className = `flex items-center gap-3 px-4 py-3 rounded-xl shadow-lg text-sm font-medium ${styles[type][0]}`;
    icon.textContent = styles[type][1];
    t.classList.remove('hidden');
    setTimeout(() => t.classList.add('hidden'), 3000);
}

// ── MODAL ──────────────────────────────────────────────
function openModal() {
    const o = document.getElementById('modalOverlay');
    o.classList.remove('hidden'); o.classList.add('flex');
}
function closeModal() {
    const o = document.getElementById('modalOverlay');
    o.classList.add('hidden'); o.classList.remove('flex');
}
document.getElementById('modalOverlay').addEventListener('click', e => {
    if (e.target === document.getElementById('modalOverlay')) closeModal();
});

// ── API HELPERS ────────────────────────────────────────
async function apiFetch(url, opts = {}) {
    const res = await fetch(url, { headers: { 'Content-Type': 'application/json' }, ...opts });
    return res.json();
}

// ── STATS ──────────────────────────────────────────────
async function loadStats() {
    const data = await apiFetch('/api/admin/stats');
    if (!data.success) return;
    const s = data.stats;
    document.getElementById('statUsers').textContent = s.total_users;
    document.getElementById('statActive').textContent = s.active_users;
    document.getElementById('statLessons').textContent = s.total_lessons;
    document.getElementById('statAvg').textContent = s.avg_points + ' XP';
}

// ── USERS TABLE ────────────────────────────────────────
async function loadUsers() {
    const search = document.getElementById('searchInput').value;
    const body = document.getElementById('usersTableBody');
    body.innerHTML = `<tr><td colspan="6" class="text-center py-8 text-gray-400">Cargando...</td></tr>`;
    const data = await apiFetch(`/api/admin/users?search=${encodeURIComponent(search)}`);
    if (!data.success) {
        body.innerHTML = `<tr><td colspan="6" class="text-center py-8 text-red-400">Error al cargar usuarios</td></tr>`;
        return;
    }
    document.getElementById('tableFooter').textContent = `${data.count} usuario(s) encontrado(s)`;
    if (data.users.length === 0) {
        body.innerHTML = `<tr><td colspan="6" class="text-center py-8 text-gray-400">No se encontraron usuarios</td></tr>`;
        return;
    }
    body.innerHTML = data.users.map(u => `
        <tr class="border-b border-gray-100 dark:border-gray-800/60 hover:bg-gray-50 dark:hover:bg-[#1c1a0e] transition-colors">
            <td class="px-5 py-3.5">
                <div class="flex items-center gap-3">
                    <div class="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-sm font-bold text-primary">
                        ${u.username.charAt(0).toUpperCase()}
                    </div>
                    <div>
                        <p class="font-medium">${escHtml(u.username)}</p>
                        <p class="text-xs text-gray-400">${u.placement_done ? '✓ Test realizado' : '— Sin test'}</p>
                    </div>
                </div>
            </td>
            <td class="px-5 py-3.5 text-gray-500 hidden md:table-cell">${escHtml(u.email)}</td>
            <td class="px-5 py-3.5 hidden sm:table-cell">
                <span class="px-2 py-0.5 rounded-full text-xs font-bold ${u.role === 'admin' ? 'bg-primary/20 text-yellow-700 dark:text-primary' : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400'}">
                    ${u.role}
                </span>
            </td>
            <td class="px-5 py-3.5 hidden lg:table-cell font-mono">${u.total_points} XP</td>
            <td class="px-5 py-3.5 hidden lg:table-cell">${u.completed_lessons}</td>
            <td class="px-5 py-3.5 text-right">
                <div class="flex items-center justify-end gap-1">
                    <button onclick="showUserDetail('${u.id}')" title="Ver detalle"
                        class="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-500">
                        <span class="material-symbols-outlined text-lg">visibility</span>
                    </button>
                    <button onclick="unlockUser('${u.id}','${escHtml(u.username)}')" title="Desbloquear lecciones"
                        class="p-1.5 rounded-lg hover:bg-green-100 dark:hover:bg-green-900/30 text-green-600">
                        <span class="material-symbols-outlined text-lg">lock_open</span>
                    </button>
                    <button onclick="resetUser('${u.id}','${escHtml(u.username)}')" title="Resetear progreso"
                        class="p-1.5 rounded-lg hover:bg-yellow-100 dark:hover:bg-yellow-900/30 text-yellow-600">
                        <span class="material-symbols-outlined text-lg">restart_alt</span>
                    </button>
                    <button onclick="toggleRole('${u.id}','${u.role}','${escHtml(u.username)}')" title="Cambiar rol"
                        class="p-1.5 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/30 text-blue-500">
                        <span class="material-symbols-outlined text-lg">manage_accounts</span>
                    </button>
                    <button onclick="deleteUser('${u.id}','${escHtml(u.username)}')" title="Eliminar usuario"
                        class="p-1.5 rounded-lg hover:bg-red-100 dark:hover:bg-red-900/30 text-red-500">
                        <span class="material-symbols-outlined text-lg">delete</span>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

// ── USER DETAIL MODAL ──────────────────────────────────
async function showUserDetail(userId) {
    document.getElementById('modalTitle').textContent = 'Detalles del usuario';
    document.getElementById('modalContent').innerHTML = '<p class="text-center text-gray-400 py-8">Cargando...</p>';
    openModal();
    const data = await apiFetch(`/api/admin/users/${userId}`);
    if (!data.success) {
        document.getElementById('modalContent').innerHTML = '<p class="text-red-400">Error al cargar</p>';
        return;
    }
    const u = data.user;
    const p = u.progress || {};
    document.getElementById('modalContent').innerHTML = `
        <div class="space-y-4">
            <div class="flex items-center gap-4">
                <div class="w-14 h-14 rounded-full bg-primary/20 flex items-center justify-center text-2xl font-bold text-primary">
                    ${(u.username || '?').charAt(0).toUpperCase()}
                </div>
                <div>
                    <p class="font-bold text-lg">${escHtml(u.username || '')}</p>
                    <p class="text-gray-500 text-sm">${escHtml(u.email || '')}</p>
                    <span class="px-2 py-0.5 rounded-full text-xs font-bold ${u.role === 'admin' ? 'bg-primary/20 text-yellow-700 dark:text-primary' : 'bg-gray-100 dark:bg-gray-800 text-gray-500'}">
                        ${u.role || 'user'}
                    </span>
                </div>
            </div>
            <div class="grid grid-cols-3 gap-3">
                ${statCard('Puntos XP', (p.total_points || 0) + ' XP', 'star')}
                ${statCard('Lecciones', (p.completed_lessons || []).length, 'menu_book')}
                ${statCard('Nivel', p.current_level || 'Básico', 'school')}
            </div>
            <div class="rounded-lg bg-gray-50 dark:bg-[#1c1a0e] p-4 text-sm space-y-2">
                <p><span class="text-gray-500">Placement test:</span> ${p.placement_test_completed ? '✅ Completado' : '❌ Pendiente'}</p>
                <p><span class="text-gray-500">Categorías desbloqueadas:</span> ${(p.unlocked_categories || ['Python Básico']).join(', ')}</p>
            </div>
            <div class="flex gap-2 flex-wrap pt-2">
                <button onclick="unlockUser('${userId}','${escHtml(u.username || '')}'); closeModal();"
                    class="flex-1 py-2 rounded-lg bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 text-sm font-bold hover:bg-green-200">
                    <span class="material-symbols-outlined text-base align-middle">lock_open</span> Desbloquear
                </button>
                <button onclick="resetUser('${userId}','${escHtml(u.username || '')}'); closeModal();"
                    class="flex-1 py-2 rounded-lg bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400 text-sm font-bold hover:bg-yellow-200">
                    <span class="material-symbols-outlined text-base align-middle">restart_alt</span> Resetear
                </button>
                <button onclick="deleteUser('${userId}','${escHtml(u.username || '')}'); closeModal();"
                    class="flex-1 py-2 rounded-lg bg-red-100 dark:bg-red-900/30 text-red-600 text-sm font-bold hover:bg-red-200">
                    <span class="material-symbols-outlined text-base align-middle">delete</span> Eliminar
                </button>
            </div>
        </div>
    `;
}

function statCard(label, value, icon) {
    return `<div class="bg-white dark:bg-[#2a2510] rounded-lg p-3 border border-gray-200 dark:border-gray-700 text-center">
        <span class="material-symbols-outlined text-primary text-xl">${icon}</span>
        <p class="font-bold mt-1">${value}</p>
        <p class="text-xs text-gray-400">${label}</p>
    </div>`;
}

// ── ACCIONES ───────────────────────────────────────────
async function unlockUser(id, name) {
    if (!confirm(`¿Desbloquear todas las lecciones para ${name}?`)) return;
    const data = await apiFetch(`/api/admin/users/${id}/unlock`, { method: 'POST' });
    showToast(data.message, data.success ? 'success' : 'error');
    if (data.success) loadUsers();
}

async function resetUser(id, name) {
    if (!confirm(`¿Resetear el progreso de ${name}? Esta acción no se puede deshacer.`)) return;
    const data = await apiFetch(`/api/admin/users/${id}/reset`, { method: 'POST' });
    showToast(data.message, data.success ? 'success' : 'error');
    if (data.success) { loadUsers(); loadStats(); }
}

async function toggleRole(id, currentRole, name) {
    const newRole = currentRole === 'admin' ? 'user' : 'admin';
    if (!confirm(`¿Cambiar rol de ${name} a "${newRole}"?`)) return;
    const data = await apiFetch(`/api/admin/users/${id}/role`, {
        method: 'PUT', body: JSON.stringify({ role: newRole })
    });
    showToast(data.message, data.success ? 'success' : 'error');
    if (data.success) loadUsers();
}

async function deleteUser(id, name) {
    if (!confirm(`¿Eliminar permanentemente al usuario ${name}? Esta acción NO se puede deshacer.`)) return;
    const data = await apiFetch(`/api/admin/users/${id}`, { method: 'DELETE' });
    showToast(data.message, data.success ? 'success' : 'error');
    if (data.success) { loadUsers(); loadStats(); }
}

async function logout() {
    await apiFetch('/api/auth/logout', { method: 'POST' });
    window.location.href = '/login';
}

function escHtml(str) {
    return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

// ── INIT ───────────────────────────────────────────────
(async () => {
    // Verificar que es admin
    let check;
    try {
        check = await apiFetch('/api/admin/check');
    } catch(e) {
        console.error('Error verificando admin:', e);
        return; // No redirigir si hay error de red
    }
    if (!check.success) { window.location.href = '/login'; return; }
    if (!check.is_admin) { window.location.href = '/course'; return; }

    // Cargar username
    const me = await apiFetch('/api/user/me');
    if (me.success) document.getElementById('adminUsername').textContent = me.user.username;

    loadStats();
    loadUsers();
})();
