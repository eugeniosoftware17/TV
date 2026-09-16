(function () {
    const config = window.CLOUD_SCREEN;
    if (!config?.previewDataUrl) return;

    const screen = document.getElementById('preview-screen');
    const content = screen?.querySelector('.preview-content');
    const btnPrev = document.getElementById('btn-prev');
    const btnNext = document.getElementById('btn-next');
    const btnPlay = document.getElementById('btn-play');

    let slides = [];
    let currentIndex = 0;
    let timer = null;
    let playing = false;

    async function loadSlides() {
        const response = await fetch(config.previewDataUrl);
        const data = await response.json();
        slides = data.slides || [];
        if (slides.length) {
            showSlide(0);
        }
    }

    function renderSlide(slide) {
        if (!content) return;
        let html = '';
        const bg = slide.background_color || '#1a1a2e';
        const bgImage = slide.background_image_url ? `background-image:url('${slide.background_image_url}');` : '';

        content.style.background = bg;
        content.style.backgroundSize = 'cover';
        content.style.backgroundPosition = 'center';
        if (bgImage) content.style.cssText += bgImage;

        if (slide.title) html += `<h2>${escapeHtml(slide.title)}</h2>`;
        if (slide.subtitle) html += `<h3>${escapeHtml(slide.subtitle)}</h3>`;

        switch (slide.type) {
            case 'image':
                if (slide.image_url) {
                    html += `<img src="${slide.image_url}" alt="">`;
                }
                break;
            case 'video':
                if (slide.video_url) {
                    html += `<video src="${slide.video_url}" controls muted></video>`;
                }
                break;
            case 'mixed':
                if (slide.content) html += `<p>${escapeHtml(slide.content)}</p>`;
                if (slide.image_url) html += `<img src="${slide.image_url}" alt="">`;
                if (slide.video_url) html += `<video src="${slide.video_url}" controls muted></video>`;
                break;
            default:
                if (slide.content) html += `<p>${escapeHtml(slide.content)}</p>`;
        }

        content.innerHTML = html || '<p class="preview-placeholder">Diapositiva vacía</p>';
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML.replace(/\n/g, '<br>');
    }

    function showSlide(index) {
        if (!slides.length) return;
        currentIndex = ((index % slides.length) + slides.length) % slides.length;
        renderSlide(slides[currentIndex]);
    }

    function stopPlay() {
        playing = false;
        if (timer) clearTimeout(timer);
        if (btnPlay) btnPlay.textContent = 'Vista previa';
    }

    function scheduleNext() {
        if (!playing || !slides.length) return;
        const duration = (slides[currentIndex].duration || 10) * 1000;
        timer = setTimeout(() => {
            showSlide(currentIndex + 1);
            scheduleNext();
        }, duration);
    }

    btnPrev?.addEventListener('click', () => { stopPlay(); showSlide(currentIndex - 1); });
    btnNext?.addEventListener('click', () => { stopPlay(); showSlide(currentIndex + 1); });

    btnPlay?.addEventListener('click', () => {
        if (playing) {
            stopPlay();
        } else {
            playing = true;
            btnPlay.textContent = 'Detener';
            scheduleNext();
        }
    });

    loadSlides();
})();
