function toggleEditMode() {
    
    const deleteButtons = document.querySelectorAll('.delete-photo');

    deleteButtons.forEach(button => {
        button.classList.toggle('visible');
    });
}

function deletePhoto(photoId) {
    if (confirm('Are you sure you want to delete this photo?')) {

        fetch(`/delete_photo/${photoId}`, {  // Send REQUEST to the URL 
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',  // Ajax Request
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ photo_id: photoId })
        })
        .then(response => {
            if (response.ok) {
                alert('Photo deleted successfully.');
                location.reload();
            } else {
                alert('Failed to delete photo.');
            }
        });
    }
}
