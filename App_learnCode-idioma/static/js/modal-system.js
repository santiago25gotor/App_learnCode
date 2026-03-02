// Modal System - Reemplaza alerts y confirms nativos
const ModalSystem = {
    // Crear modal en el DOM si no existe
    init() {
        if (document.getElementById('customModalOverlay')) return;

        const overlay = document.createElement('div');
        overlay.id = 'customModalOverlay';
        overlay.className = 'fixed inset-0 bg-black/50 backdrop-blur-sm z-50 hidden items-center justify-center p-4';
        overlay.innerHTML = `
            <div id="customModalContainer" class="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl max-w-md w-full transform transition-all scale-95 opacity-0">
                <div id="customModalHeader" class="p-6 border-b border-gray-200 dark:border-gray-800">
                    <div class="flex items-center gap-3">
                        <div id="customModalIcon" class="w-12 h-12 rounded-full flex items-center justify-center">
                            <span class="material-symbols-outlined text-2xl"></span>
                        </div>
                        <h3 id="customModalTitle" class="text-xl font-bold"></h3>
                    </div>
                </div>
                <div id="customModalBody" class="p-6">
                    <p id="customModalMessage" class="text-gray-700 dark:text-gray-300"></p>
                </div>
                <div id="customModalFooter" class="p-6 border-t border-gray-200 dark:border-gray-800 flex gap-3 justify-end">
                    <!-- Buttons will be added dynamically -->
                </div>
            </div>
        `;
        document.body.appendChild(overlay);

        // Cerrar con click fuera del modal
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                this.close();
            }
        });
    },

    // Mostrar modal genérico
    show({ type = 'info', title, message, buttons = [], onClose }) {
        this.init();

        const overlay = document.getElementById('customModalOverlay');
        const container = document.getElementById('customModalContainer');
        const icon = document.getElementById('customModalIcon');
        const titleEl = document.getElementById('customModalTitle');
        const messageEl = document.getElementById('customModalMessage');
        const footer = document.getElementById('customModalFooter');

        // Configurar según tipo
        const configs = {
            success: {
                iconBg: 'bg-green-100 dark:bg-green-900/30',
                iconColor: 'text-green-600',
                icon: 'check_circle'
            },
            error: {
                iconBg: 'bg-red-100 dark:bg-red-900/30',
                iconColor: 'text-red-600',
                icon: 'error'
            },
            warning: {
                iconBg: 'bg-yellow-100 dark:bg-yellow-900/30',
                iconColor: 'text-yellow-600',
                icon: 'warning'
            },
            info: {
                iconBg: 'bg-blue-100 dark:bg-blue-900/30',
                iconColor: 'text-blue-600',
                icon: 'info'
            },
            question: {
                iconBg: 'bg-purple-100 dark:bg-purple-900/30',
                iconColor: 'text-purple-600',
                icon: 'help'
            }
        };

        const config = configs[type] || configs.info;

        // Aplicar estilos
        icon.className = `w-12 h-12 rounded-full flex items-center justify-center ${config.iconBg}`;
        icon.querySelector('span').className = `material-symbols-outlined text-2xl ${config.iconColor}`;
        icon.querySelector('span').textContent = config.icon;

        titleEl.textContent = title;
        messageEl.textContent = message;

        // Crear botones
        footer.innerHTML = '';
        buttons.forEach(btn => {
            const button = document.createElement('button');
            button.className = `px-6 py-2.5 rounded-lg font-bold transition-all ${btn.primary ? 'bg-primary hover:bg-yellow-400 text-black' : 'bg-gray-200 dark:bg-gray-800 hover:bg-gray-300 dark:hover:bg-gray-700 text-gray-900 dark:text-white'}`;
            button.textContent = btn.text;
            button.onclick = () => {
                if (btn.onClick) btn.onClick();
                this.close();
                if (onClose) onClose();
            };
            footer.appendChild(button);
        });

        // Mostrar con animación
        overlay.classList.remove('hidden');
        overlay.classList.add('flex');
        setTimeout(() => {
            container.classList.remove('scale-95', 'opacity-0');
            container.classList.add('scale-100', 'opacity-100');
        }, 10);
    },

    // Cerrar modal
    close() {
        const overlay = document.getElementById('customModalOverlay');
        const container = document.getElementById('customModalContainer');

        if (!overlay) return;

        container.classList.add('scale-95', 'opacity-0');
        container.classList.remove('scale-100', 'opacity-100');

        setTimeout(() => {
            overlay.classList.add('hidden');
            overlay.classList.remove('flex');
        }, 200);
    },

    // Alert personalizado
    alert({ type = 'info', title, message }) {
        return new Promise((resolve) => {
            this.show({
                type,
                title,
                message,
                buttons: [
                    { text: 'Aceptar', primary: true, onClick: resolve }
                ],
                onClose: resolve
            });
        });
    },

    // Confirm personalizado
    confirm({ type = 'question', title, message, confirmText = 'Confirmar', cancelText = 'Cancelar' }) {
        return new Promise((resolve) => {
            this.show({
                type,
                title,
                message,
                buttons: [
                    { text: cancelText, primary: false, onClick: () => resolve(false) },
                    { text: confirmText, primary: true, onClick: () => resolve(true) }
                ],
                onClose: () => resolve(false)
            });
        });
    },

    // Success shortcut
    success(message, title = '¡Éxito!') {
        return this.alert({ type: 'success', title, message });
    },

    // Error shortcut
    error(message, title = 'Error') {
        return this.alert({ type: 'error', title, message });
    },

    // Warning shortcut
    warning(message, title = 'Advertencia') {
        return this.alert({ type: 'warning', title, message });
    },

    // Info shortcut
    info(message, title = 'Información') {
        return this.alert({ type: 'info', title, message });
    }
};

// Hacer global
window.Modal = ModalSystem;