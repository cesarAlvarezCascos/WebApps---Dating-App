document.addEventListener('DOMContentLoaded', function () {
    const datePicker = document.getElementById('selected-date');
    const restaurantList = document.getElementById('restaurant-list');

    datePicker.addEventListener('change', function () {
        const selectedDate = datePicker.value;
        
        fetch(`/restaurants_availability/${selectedDate}`)
            .then(response => response.json())
            .then(data => {
                restaurantList.innerHTML = ''; // Clear the list

                if (data.error) {
                    restaurantList.innerHTML = `<p class="error-message">${data.error}</p>`;
                } else if (data.is_past){ 
                    restaurantList.innerHTML = '<p class="no-results">You cannot schedule a date in the past.</p>';

                } else if (data.restaurants && data.restaurants.length === 0) {
                    restaurantList.innerHTML = '<p class="no-results">No restaurants available for the selected date.</p>';
                }  else {
                    const form = document.createElement('form');
                    form.setAttribute('id', 'schedule-date-form');
                    form.setAttribute('action', '/schedule_date_action');
                    form.setAttribute('method', 'POST');

                    // Add hidden inputs
                    const dateInput = document.createElement('input');
                    dateInput.setAttribute('type', 'hidden');
                    dateInput.setAttribute('name', 'proposed_date');
                    dateInput.setAttribute('value', selectedDate);
                    form.appendChild(dateInput);

                    const otherUserIdInput = document.createElement('input');
                    otherUserIdInput.setAttribute('type', 'hidden');
                    otherUserIdInput.setAttribute('name', 'other_user_id');
                    const otherUserId = document.getElementById('available-restaurants').getAttribute('data-user-id');
                    otherUserIdInput.setAttribute('value', otherUserId);
                    form.appendChild(otherUserIdInput);

                    // Add textarea for the message
                    const messageLabel = document.createElement('label');
                    messageLabel.textContent = "Write your proposal message:";
                    form.appendChild(messageLabel);

                    const messageTextarea = document.createElement('textarea');
                    messageTextarea.setAttribute('name', 'message');
                    messageTextarea.setAttribute('placeholder', 'Write a message for your date...');
                    form.appendChild(messageTextarea);

                    // Add restaurant choices
                    const restaurantLabel = document.createElement('p');
                    restaurantLabel.textContent = "Choose a restaurant:";
                    form.appendChild(restaurantLabel);

                    data.restaurants.forEach(restaurant => {
                        const wrapper = document.createElement('div');
                        wrapper.classList.add('radio-group');

                        const radio = document.createElement('input');
                        radio.setAttribute('type', 'radio');
                        radio.setAttribute('name', 'restaurant_id');
                        radio.setAttribute('value', restaurant.id);
                        radio.setAttribute('id', `restaurant-${restaurant.id}`);
                        wrapper.appendChild(radio);

                        const label = document.createElement('label');
                        label.setAttribute('for', `restaurant-${restaurant.id}`);
                        label.textContent = `${restaurant.name} (${restaurant.slots} slots available)`;
                        wrapper.appendChild(label);

                        form.appendChild(wrapper);
                    });

                    // Add submit button
                    const submitButton = document.createElement('button');
                    submitButton.setAttribute('type', 'submit');
                    submitButton.textContent = "Schedule Date";
                    form.appendChild(submitButton);

                    restaurantList.appendChild(form);
                }
            })
            .catch(error => {
                console.error('Error fetching restaurants:', error);
                restaurantList.innerHTML = `<p class="error-message">Failed to fetch restaurant data. Please try again later.</p>`;
            });
    });
});



