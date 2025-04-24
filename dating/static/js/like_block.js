
document.addEventListener('DOMContentLoaded', function () {

    // Get buttons and user ID from the data attributes
    const likeButton = document.getElementById('likeButton');
    const blockButton = document.getElementById('blockButton');
    const scheduleDateButton = document.getElementById('scheduleDateButton');
    const userId = likeButton.getAttribute('data-user-id');  // Get user ID from the data attribute

    // Get initial states (liked and blocked)
    const likedUserIds = likeButton.getAttribute('data-liked');
    const blockedUserIds = blockButton.getAttribute('data-blocked');
    const scheduleDateContainer = document.getElementById('scheduleDateContainer');
    //console.log("Initial data-liked", likeButton.getAttribute('data-liked'))
    console.log("Initial data-blocked", blockButton.getAttribute('data-blocked'))

    const initialLikedState = likedUserIds.includes(userId);
    const initialBlockedState = blockedUserIds.includes(userId);

    // Set the initial color of the buttons based on the states
    setLikeButtonState(initialLikedState);
    setBlockButtonState(initialBlockedState);

    // CHECK MATCH: if like relationship is bidirectional
    function isBidirectionalLike(logged_user_like_state) {
        const conditioncheck = otherUserLikesLoggedUser();
        const conditioncheck2 = previousDateReschedule();
        console.log("Reschedule", conditioncheck2)
        return logged_user_like_state && conditioncheck && conditioncheck2;
    }
    function previousDateReschedule() {
        const latestProposalStatus =String(scheduleDateButton.getAttribute('data-latest-proposal-status')).trim();
        console.log("Latest date status", latestProposalStatus)

        if (latestProposalStatus === "reschedule" | latestProposalStatus === "None" ){
            return true
        } 
        else{
            return false
        } 
    } 

    
    
    function otherUserLikesLoggedUser() {
        const loggedUserId = parseInt(scheduleDateButton.getAttribute('data-logged-user-id'));
        console.log("Logged user id",loggedUserId)
        const otherUserLikingIds = scheduleDateButton.getAttribute('data-user-liking-ids');
        console.log("OtherUserLikingIds",otherUserLikingIds)
        console.log("Like condition state", otherUserLikingIds.includes(loggedUserId))

        return otherUserLikingIds.includes(loggedUserId);
    }

    // Initial visibility of the 'Schedule a Date' button
    toggleScheduleDateButton(isBidirectionalLike(initialLikedState),userId);
    // Add event listeners for button clicks
    likeButton.addEventListener('click', function() {
        toggleLike(userId);
    });

    blockButton.addEventListener('click', function() {
        toggleBlock(userId);
    });


    // Function to toggle the like state (like/unlike)
    function toggleLike(userId) {
        console.log("Toggling like for user with ID:", userId);
        fetch('/like/' + userId, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ user_id: userId })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showNotification(data.error); // Muestra el mensaje de error
            } else  {
            console.log(data);  // Handle the server response
            // Toggle like button color based on the response
            setLikeButtonState(data.liked);
            const otherUserLikeState = otherUserLikesLoggedUser(); 
            const otherDatesState = previousDateReschedule(); 
            const bidirectional = data.liked && otherUserLikeState && otherDatesState;
            //console.log("Bidirectional state", otherUserLikeState)
            toggleScheduleDateButton(bidirectional,userId);
            } 
        })
        .catch(error => {
            console.error('Error toggling like:', error);
        });
    }

    // Function to toggle the block state (block/unblock)
    function toggleBlock(userId) {
        console.log("Toggling block for user with ID:", userId);
        fetch('/block/' + userId, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ user_id: userId })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showNotification(data.error); // Muestra el mensaje de error
            } else {
            console.log(data);  // Handle the server response
            // Toggle block button color based on the response
            setBlockButtonState(data.blocked);
            } 
        })
        .catch(error => {
            console.error('Error toggling block:', error);
        });
    }

    // Function to update the like button state (green for liked, white for unliked)
    function setLikeButtonState(isLiked) {
        if (isLiked) {
            likeButton.classList.add('liked');
            likeButton.classList.remove('unliked');
        } else {
            likeButton.classList.add('unliked');
            likeButton.classList.remove('liked');
        }
    }

    // Function to update the block button state (red for blocked, white for unblocked)
    function setBlockButtonState(isBlocked) {
        if (isBlocked) {
            blockButton.classList.add('blocked');
            blockButton.classList.remove('unblocked');
            
        } else {
            blockButton.classList.add('unblocked');
            blockButton.classList.remove('blocked');
        }
    }

    // Function to show notifications when user can't block/like another user
    
    function showNotification(message) {
        // Check if a notification is already being displayed
       const displayednot = document.querySelector('.notification');
       if (displayednot) {
           displayednot.remove();
       }
       const messageDiv = document.createElement('div');
       messageDiv.className = 'notification';
       messageDiv.textContent = message;
       const container = document.querySelector('.buttons-container');
       if (blockButton){
           container.insertBefore(messageDiv, blockButton.nextSibling); 
       } 
       
       setTimeout(() => messageDiv.remove(), 1500); // Remove after 3 seconds
    }    

    // Function to toggle the "Schedule a Date" button visibility and set href
    function toggleScheduleDateButton(isVisible, userId) {
        if (isVisible) {
            scheduleDateButton.setAttribute('href', `/schedule_date/${userId}`);
            scheduleDateContainer.classList.remove('hidden');
        } else {
            scheduleDateButton.removeAttribute('href');
            scheduleDateContainer.classList.add('hidden');
        }
    }

    


});
    



