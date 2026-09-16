(function () {
    const panel = document.getElementById('import-status-panel');
    if (!panel) return;

    const statusUrl = panel.dataset.statusUrl;
    const icon = document.getElementById('status-icon');
    const title = document.getElementById('status-title');
    const message = document.getElementById('status-message');
    const progressFill = document.getElementById('progress-fill');
    const progressText = document.getElementById('progress-text');
    const successBlock = document.getElementById('status-success');
    const errorBlock = document.getElementById('status-error');
    const errorMessage = document.getElementById('error-message');
    const editorLink = document.getElementById('editor-link');
    const progressBar = document.getElementById('progress-bar');

    let pollTimer = null;

    function updateUI(data) {
        const total = data.slide_count || 0;
        const processed = data.processed_slide_count || 0;

        if (data.status === 'processing' || data.status === 'pending') {
            title.textContent = 'Procesando presentación...';
            if (total > 0) {
                message.textContent = `Procesando ${total} diapositiva${total !== 1 ? 's' : ''}...`;
                const pct = Math.min(100, Math.round((processed / total) * 100));
                progressFill.style.width = `${pct}%`;
                progressText.textContent = processed > 0 ? `${processed} de ${total}` : '';
            } else {
                message.textContent = 'Analizando archivo PowerPoint...';
                progressFill.style.width = '30%';
            }
        }

        if (data.status === 'completed') {
            clearInterval(pollTimer);
            icon.textContent = '✓';
            icon.className = 'ppt-status-icon success';
            title.textContent = 'Presentación importada';
            message.classList.add('hidden');
            progressBar.classList.add('hidden');
            progressText.classList.add('hidden');
            successBlock.classList.remove('hidden');
            if (editorLink && data.editor_url) {
                editorLink.href = data.editor_url;
            }
        }

        if (data.status === 'failed') {
            clearInterval(pollTimer);
            icon.textContent = '✕';
            icon.className = 'ppt-status-icon error';
            title.textContent = 'Error en la importación';
            message.classList.add('hidden');
            progressBar.classList.add('hidden');
            progressText.classList.add('hidden');
            errorBlock.classList.remove('hidden');
            errorMessage.textContent = data.error_message || 'No fue posible procesar este archivo PowerPoint.';
        }
    }

    async function poll() {
        try {
            const response = await fetch(statusUrl, { cache: 'no-store' });
            const data = await response.json();
            updateUI(data);
        } catch (err) {
            console.error('Error consultando estado:', err);
        }
    }

    poll();
    pollTimer = setInterval(poll, 2000);
})();
