document.addEventListener('DOMContentLoaded', function () {
    const imageInput = document.querySelector('input[type="file"][name="image"]');
    if (!imageInput) return;

    const previewContainer = document.createElement('div');
    previewContainer.className = 'vendor-image-preview';
    imageInput.parentNode.appendChild(previewContainer);

    const previewImg = document.createElement('img');
    previewImg.className = 'vendor-preview-img';
    previewImg.alt = 'Selected product image preview';
    previewContainer.appendChild(previewImg);

    const removeBtn = document.createElement('button');
    removeBtn.type = 'button';
    removeBtn.textContent = 'Clear Selection';
    removeBtn.className = 'vendor-remove-img-btn';
    previewContainer.appendChild(removeBtn);

    const currentImage = imageInput.dataset.currentImage;
    removeBtn.hidden = true;

    const showPreview = function (src, canClear) {
        previewImg.src = src;
        previewContainer.classList.add('is-visible');
        removeBtn.hidden = !canClear;
    };

    const showCurrentImage = function () {
        if (currentImage) {
            showPreview(currentImage, false);
        } else {
            previewImg.src = '';
            previewContainer.classList.remove('is-visible');
            removeBtn.hidden = true;
        }
    };

    if (currentImage) {
        showCurrentImage();
    }

    imageInput.addEventListener('change', function (e) {
        const file = e.target.files[0];
        if (file && file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = function (evt) {
                showPreview(evt.target.result, true);
            };
            reader.readAsDataURL(file);
        } else {
            showCurrentImage();
        }
    });

    removeBtn.addEventListener('click', function () {
        imageInput.value = '';
        showCurrentImage();
    });
});
