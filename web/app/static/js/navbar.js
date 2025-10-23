document.addEventListener('DOMContentLoaded', function() {
    const themeToggle = document.getElementById('theme-toggle');
    const themeIcon = document.getElementById('theme-icon');
    const htmlElement = document.documentElement;

    const savedTheme = localStorage.getItem('theme') || 'dark';
    htmlElement.setAttribute('data-bs-theme', savedTheme);
    updateToggleButton(savedTheme);
    
    themeToggle.addEventListener('click', function() {
        const currentTheme = htmlElement.getAttribute('data-bs-theme');
        const newTheme = currentTheme === 'dark' ? 'custom-dark' : 'dark';

        htmlElement.setAttribute('data-bs-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateToggleButton(newTheme);
    });
    
    function updateToggleButton(theme) {
        if (theme === 'dark') {
            themeToggle.classList.remove('btn-secondary');
            themeToggle.classList.add('btn-light');
            themeIcon.textContent = '☀️';
        } else {
            themeToggle.classList.remove('btn-light');
            themeToggle.classList.add('btn-secondary');
            themeIcon.textContent = '🌙';
        }
    }
});
