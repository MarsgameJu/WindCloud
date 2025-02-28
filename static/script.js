document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.getElementById('theme-toggle');
    const icon = themeToggle.querySelector('i');

    function updateThemeIcon(isDark) {
        icon.classList.remove('fa-sun', 'fa-moon');
        if (isDark) {
            icon.classList.add('fa-sun');
        } else {
            icon.classList.add('fa-moon');
        }
    }

    themeToggle.addEventListener('click', () => {
        const isDark = document.body.classList.contains('dark-mode');
        document.body.classList.toggle('dark-mode');
        document.body.classList.toggle('light-mode');
        
        updateThemeIcon(!isDark);
        localStorage.setItem('theme', !isDark ? 'dark' : 'light');
    });

    // Check saved preference
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.body.classList.remove('dark-mode', 'light-mode');
    document.body.classList.add(savedTheme === 'dark' ? 'dark-mode' : 'light-mode');
    updateThemeIcon(savedTheme === 'dark');

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
});
