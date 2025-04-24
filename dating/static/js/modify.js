// PREVIEW IMAGE

document.getElementById('profile-pic').addEventListener('change', function(event) {
    const file = event.target.files[0]; // Selected pic
    const previewContainer =  document.getElementById('profile-pic-preview'); // img container

    if (file) {
        const reader = new FileReader();

        reader.onload = function(e) {
            if (previewContainer.id === 'profile-pic-preview') { // Modify, just update the src of the image
                
                previewContainer.src = e.target.result;
            }
        };

        reader.readAsDataURL(file); 
    } 
});


function updateAgeRange() {
    const birthYearInput = document.getElementById('birth');
    const minAgeDiffInput = document.getElementById('min_age_diff');
    const maxAgeDiffInput = document.getElementById('max_age_diff');

    const birthYear = parseInt(birthYearInput.value, 10);
    const minAgeDiff = parseInt(minAgeDiffInput.value, 10);
    const maxAgeDiff = parseInt(maxAgeDiffInput.value, 10);

    const currentYear = new Date().getFullYear();
    const warningMessage = document.getElementById('age-warning');

    if (!isNaN(birthYear)) {
        const currentAge = currentYear - birthYear;

        if (!isNaN(minAgeDiff)) {
            const youngestAge = currentAge - minAgeDiff;
            document.getElementById('youngest-age').textContent = `Youngest: ${youngestAge}`;

            if (youngestAge <= 18) {
                minAgeDiffInput.max = minAgeDiff; // Block increasing the value
                warningMessage.textContent = 'Youngest age cannot be below 18.';
                warningMessage.style.display = 'block';
            } else {
                warningMessage.style.display = 'none';
            }
        } else {
            document.getElementById('youngest-age').textContent = '';
        }

        if (!isNaN(maxAgeDiff)) {
            const oldestAge = currentAge + maxAgeDiff;
            document.getElementById('oldest-age').textContent = `Oldest: ${oldestAge}`;
        } else {
            document.getElementById('oldest-age').textContent = '';
        }
    } else {
        document.getElementById('youngest-age').textContent = '';
        document.getElementById('oldest-age').textContent = '';
        warningMessage.style.display = 'none';
    }
}


document.addEventListener('DOMContentLoaded', updateAgeRange);
document.getElementById('birth').addEventListener('input', updateAgeRange);
document.getElementById('min_age_diff').addEventListener('input', updateAgeRange);
document.getElementById('max_age_diff').addEventListener('input', updateAgeRange);