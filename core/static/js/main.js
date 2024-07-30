// core/static/core/js/main.js

// Sayfa yüklendiğinde çalışacak fonksiyon
document.addEventListener('DOMContentLoaded', function() {
    console.log('Restaurant POS system loaded');
    
    // Örnek: Navbar'daki aktif linki vurgulama
    const currentLocation = location.href;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    navLinks.forEach(link => {
        if (link.href === currentLocation) {
            link.classList.add('active');
        }
    });
});