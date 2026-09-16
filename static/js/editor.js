(function () {
    const slideList = document.getElementById('slide-list');
    if (!slideList || typeof Sortable === 'undefined') return;

    const reorderUrl = slideList.dataset.reorderUrl;
    const csrfToken = window.CLOUD_SCREEN?.csrfToken;

    Sortable.create(slideList, {
        handle: '.drag-handle',
        animation: 150,
        ghostClass: 'sortable-ghost',
        chosenClass: 'sortable-chosen',
        filter: '.empty-slides',
        onEnd: async function () {
            const items = slideList.querySelectorAll('.slide-item[data-id]');
            const order = Array.from(items).map(el => parseInt(el.dataset.id, 10));

            items.forEach((el, idx) => {
                const num = el.querySelector('.slide-number');
                if (num) num.textContent = idx + 1;
            });

            try {
                const response = await fetch(reorderUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken,
                    },
                    body: JSON.stringify({ order }),
                });
                if (!response.ok) {
                    console.error('Error al reordenar diapositivas');
                }
            } catch (err) {
                console.error('Error de red al reordenar:', err);
            }
        },
    });
})();
