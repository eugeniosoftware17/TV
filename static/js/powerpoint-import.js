(function () {
    const dropzone = document.getElementById('ppt-dropzone');
    const fileInput = document.getElementById('id_powerpoint_file');
    const selectedLabel = document.getElementById('ppt-selected-file');
    const form = document.getElementById('ppt-import-form');
    const submitBtn = document.getElementById('ppt-submit-btn');
    const fileBtn = document.querySelector('.ppt-file-btn');

    if (!dropzone || !fileInput) return;

    fileBtn?.addEventListener('click', (e) => {
        e.preventDefault();
        fileInput.click();
    });

    fileInput.addEventListener('change', () => {
        if (fileInput.files.length) {
            selectedLabel.textContent = fileInput.files[0].name;
            selectedLabel.classList.remove('hidden');
        }
    });

    ['dragenter', 'dragover'].forEach((eventName) => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            dropzone.classList.add('dragover');
        });
    });

    ['dragleave', 'drop'].forEach((eventName) => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            dropzone.classList.remove('dragover');
        });
    });

    dropzone.addEventListener('drop', (e) => {
        const files = e.dataTransfer?.files;
        if (files && files.length) {
            const dt = new DataTransfer();
            dt.items.add(files[0]);
            fileInput.files = dt.files;
            selectedLabel.textContent = files[0].name;
            selectedLabel.classList.remove('hidden');
        }
    });

    form?.addEventListener('submit', () => {
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.textContent = 'Subiendo...';
        }
    });
})();
