(function () {
    const config = window.CLOUD_SCREEN_TV;
    if (!config?.dataUrl) return;

    const slideEl = document.getElementById('tv-slide');
    const offlineEl = document.getElementById('tv-offline');

    let slides = [];
    let currentIndex = 0;
    let timer = null;
    let currentVersion = 0;
    let pollInterval = null;
    let isOnline = navigator.onLine;

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML.replace(/\n/g, '<br>');
    }

    function renderSlide(slide) {
        const bg = slide.background_color || '#1a1a2e';
        slideEl.style.backgroundColor = bg;
        slideEl.style.backgroundImage = slide.background_image_url
            ? `url('${slide.background_image_url}')`
            : 'none';
        slideEl.style.backgroundSize = 'cover';
        slideEl.style.backgroundPosition = 'center';

        let html = '';
        if (slide.title) html += `<h1>${escapeHtml(slide.title)}</h1>`;
        if (slide.subtitle) html += `<h2>${escapeHtml(slide.subtitle)}</h2>`;

        switch (slide.type) {
            case 'image':
                if (slide.image_url) html += `<img src="${slide.image_url}" alt="">`;
                break;
            case 'video':
                if (slide.video_url) {
                    html += `<video id="tv-video" src="${slide.video_url}" autoplay muted playsinline></video>`;
                }
                break;
            case 'mixed':
                if (slide.content) html += `<p>${escapeHtml(slide.content)}</p>`;
                if (slide.image_url) html += `<img src="${slide.image_url}" alt="">`;
                if (slide.video_url) {
                    html += `<video id="tv-video" src="${slide.video_url}" autoplay muted playsinline></video>`;
                }
                break;
            default:
                if (slide.content) html += `<p>${escapeHtml(slide.content)}</p>`;
        }

        slideEl.classList.add('fade-out');
        setTimeout(() => {
            slideEl.innerHTML = html;
            slideEl.classList.remove('fade-out');

            const video = document.getElementById('tv-video');
            if (video) {
                video.play().catch(() => {});
                video.onended = () => advanceSlide();
                return;
            }
            scheduleNext(slide.duration || 10);
        }, 300);
    }

    function scheduleNext(seconds) {
        if (timer) clearTimeout(timer);
        timer = setTimeout(advanceSlide, seconds * 1000);
    }

    function advanceSlide() {
        if (!slides.length) return;
        currentIndex = (currentIndex + 1) % slides.length;
        renderSlide(slides[currentIndex]);
    }

    function startPlayback() {
        if (!slides.length) {
            slideEl.innerHTML = '<div class="tv-loading">Sin diapositivas</div>';
            return;
        }
        currentIndex = 0;
        renderSlide(slides[0]);
    }

    async function fetchPresentation() {
        try {
            const response = await fetch(config.dataUrl, { cache: 'no-store' });
            if (!response.ok) throw new Error('Fetch failed');
            const data = await response.json();

            setOnline(true);

            if (data.version !== currentVersion) {
                currentVersion = data.version;
                slides = data.slides || [];
                if (timer) clearTimeout(timer);
                startPlayback();
            }
        } catch (err) {
            setOnline(false);
        }
    }

    function setOnline(online) {
        isOnline = online;
        if (offlineEl) {
            offlineEl.classList.toggle('hidden', online);
        }
    }

    function keepAwake() {
        let wakeLock = null;
        async function requestWakeLock() {
            try {
                if ('wakeLock' in navigator) {
                    wakeLock = await navigator.wakeLock.request('screen');
                }
            } catch (e) { /* not supported on all TVs */ }
        }
        requestWakeLock();
        document.addEventListener('visibilitychange', () => {
            if (document.visibilityState === 'visible') requestWakeLock();
        });
    }

    function init() {
        keepAwake();
        fetchPresentation();

        pollInterval = setInterval(fetchPresentation, 30000);

        window.addEventListener('online', () => {
            setOnline(true);
            fetchPresentation();
        });
        window.addEventListener('offline', () => setOnline(false));

        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowRight') advanceSlide();
            if (e.key === 'ArrowLeft') {
                currentIndex = (currentIndex - 1 + slides.length) % slides.length;
                renderSlide(slides[currentIndex]);
            }
        });
    }

    init();
})();
