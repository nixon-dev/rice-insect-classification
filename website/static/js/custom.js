document.getElementById('upload-form').addEventListener('submit', async (event) => {
    event.preventDefault();

    const formData = new FormData();
    const fileInput = document.getElementById('file-input');
    const userId = document.getElementById('useridText');
    const imageFile = document.getElementById('file-input').files[0];

    formData.append('userId', userId.value);

    try {
        // Resize the image to 640 width and auto height
        const resizedImage = await resizeImage(imageFile, 640);

        const base64String = await convertImageToBase64(resizedImage);
        const base64StringWithoutHeader = base64String.split(',')[1];
        formData.append('base64', base64StringWithoutHeader);
        formData.append('file', imageFile);

        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.error) {
            alert('Error: ' + data.error);
        } else {
            window.location.href = `/result?image=${encodeURIComponent(data.image)}&insect_name=${encodeURIComponent(data.insect_name)}`;
        }
    } catch (error) {
        console.error('Error uploading image:', error);
        alert('Error uploading image. Please try again.');
    }
});

function convertImageToBase64(image) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(image);
        reader.onload = () => resolve(reader.result);
        reader.onerror = error => reject(error);
    });
}

async function resizeImage(file, maxWidth) {
    return new Promise((resolve, reject) => {
        const img = new Image();
        img.src = URL.createObjectURL(file);

        img.onload = () => {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');

            const scaleFactor = Math.min(maxWidth / img.width, 1);
            const newWidth = img.width * scaleFactor;
            const newHeight = img.height * scaleFactor;

            canvas.width = newWidth;
            canvas.height = newHeight;

            ctx.drawImage(img, 0, 0, newWidth, newHeight);

            canvas.toBlob(blob => {
                URL.revokeObjectURL(img.src);
                resolve(blob);
            }, 'image/jpeg');
        };

        img.onerror = error => reject(error);
    });
}