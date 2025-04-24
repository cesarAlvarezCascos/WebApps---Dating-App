
function showAddPhotoForm() {
    var form = document.getElementById('add-photo-form');
    form.classList.toggle('visible')
}

document.addEventListener('click', function(event) {
    var form = document.getElementById('add-photo-form');
    var button = document.querySelector('.add-photo-button');

    // Verifica si el clic fue fuera del formulario y el botón
    if (form.classList.contains('visible') && !form.contains(event.target) && event.target !== button) {
        form.classList.remove('visible');
    }
});

// PREVIEW PHOTO
document.getElementById('photo-input').addEventListener('change', function(event) {
    const file = event.target.files[0];
    const previewContainer = document.getElementById('photo-preview');
    
    // Clear preview container before loading the photo
    previewContainer.innerHTML = '';

    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const img = document.createElement('img');
            img.src = e.target.result;
            img.style.maxWidth = '100%'; 
            img.style.height = 'auto';
            previewContainer.appendChild(img);
        };
        reader.readAsDataURL(file);
    } else {
        previewContainer.innerHTML = '<em>No image selected.</em>';
    }
});



// PHOTO FULL SIZE VIEW 


function showFullPhoto(imgElement) {

    const largePhoto = document.getElementById('fullPhoto');
    largePhoto.src = imgElement.src;  // clicked image's source

    // Show the photo container
    const container = document.getElementById('fullPhotoBlock');
    container.style.display = 'flex';

    // Event Listener while we have the Fulll Size View
    document.addEventListener('keydown', handleEscapeKey);
}

function hideFullPhoto() {
    // Hide the photo container
    const container = document.getElementById('fullPhotoBlock');
    container.style.display = 'none';

    document.removeEventListener('keydown', handleEscapeKey);
}

function handleEscapeKey(event) {
    if (event.key === 'Escape') {
        hideFullPhoto();
    }
}