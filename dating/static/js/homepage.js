let showAll = false; 

function toggleView() {
    showAll = !showAll; 
    const button = document.getElementById('toggleViewButton');
    button.textContent = showAll ? 'Apply My Preferences' : 'Show All';

    // Use backticks for string interpolation
    fetch(`/?showAll=${showAll}`)
        .then(response => response.text())
        .then(html => {
            const profilesContainer = document.querySelector('.profiles-container');
            const parser = new DOMParser();
            const newDocument = parser.parseFromString(html, 'text/html');
            const newProfiles = newDocument.querySelector('.profiles-container');
            if (newProfiles) {
                profilesContainer.innerHTML = newProfiles.innerHTML;
            } else {
                console.error('Error: .profiles-container not found in the response HTML');
            }
        })
        .catch(error => console.error('Error fetching profiles:', error));
}

document.addEventListener('DOMContentLoaded', function () {
    console.log("Homepage actions loaded!");

    // Attach event listeners to all like buttons
    document.querySelectorAll('.like-button').forEach(button => {
        button.addEventListener('click', function (event) {
            event.preventDefault(); // Prevent default button behavior
            const userId = button.getAttribute('data-user-id'); // Get user ID from button attribute
            toggleLike(userId, button); // Call toggleLike with the specific button
        });
    });

    // Function to toggle the like state
    function toggleLike(userId, button) {
        console.log("Toggling like for user with ID:", userId);

        fetch(`/like/${userId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ user_id: userId }) // Send user ID in the request body
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error toggling like:', data.error);
                showNotification(data.error); // Show error notification
            } else {
                console.log('Like status updated:', data.liked);
                updateLikeButton(button, data.liked); // Update button state based on like status
            }
        })
        .catch(error => {
            console.error('Error toggling like:', error);
        });
    }

    // Function to update the like button's state
    function updateLikeButton(button, isLiked) {
        if (isLiked) {
            button.classList.add('liked');
            button.classList.remove('unliked');
            button.innerHTML = '<i class="fas fa-heart nav-icon"></i> Liked';
        } else {
            button.classList.add('unliked');
            button.classList.remove('liked');
            button.innerHTML = '<i class="fas fa-heart nav-icon"></i> Like';
        }
    }

    // Function to show notifications
    function showNotification(message) {
        const notification = document.createElement('div');
        notification.className = 'notification';
        notification.textContent = message;
        document.body.appendChild(notification);

        // Remove notification after 2 seconds
        setTimeout(() => notification.remove(), 2000);
    }
});
