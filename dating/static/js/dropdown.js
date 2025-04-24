function toggleDropdown(dropdownId) {
    
    // Get all dropdowns' contents (class = dropdown-content)
    const dropdowns = document.querySelectorAll('.dropdown-content');

    // Close all other dropdowns if open
    dropdowns.forEach(dropdown => {
        if (dropdown.id !== dropdownId) {
            dropdown.classList.remove('show');
        }
    });

    // Toggle the clicked dropdown class 'show'
    const dropdown = document.getElementById(dropdownId);
    dropdown.classList.toggle('show');
}

// Close the dropdown if the user clicks outside of it
window.onclick = function(event) {
    if (!event.target.matches('.nav-button') && !event.target.closest('.dropdown')) {
        const dropdowns = document.querySelectorAll('.dropdown-content');
        dropdowns.forEach(dropdown => {
            dropdown.classList.remove('show');
        });
    }
};



