// Update date in the header
document.addEventListener('DOMContentLoaded', function() {
    const dateElement = document.querySelector('.date');
    const options = { weekday: 'short', day: '2-digit', month: '2-digit', year: 'numeric' };
    const currentDate = new Date().toLocaleDateString('en-GB', options);
    dateElement.textContent = currentDate;
});
