document.addEventListener('DOMContentLoaded', function() {

    // --- ANIMACIÓN AL HACER SCROLL ---
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, {
        threshold: 0.1 // El elemento se considera visible cuando el 10% está en pantalla
    });

    const elementsToAnimate = document.querySelectorAll('.animate-on-scroll');
    elementsToAnimate.forEach(el => observer.observe(el));


    // --- FILTRO DE PRODUCTOS ---
    const filterButtons = document.querySelectorAll('.filter-btn');
    const productItems = document.querySelectorAll('.product-item');

    filterButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Manejar el estado activo del botón
            filterButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');

            const filter = button.getAttribute('data-filter');

            productItems.forEach(item => {
                // Ocultar todos los items
                item.style.display = 'none';
                item.classList.remove('visible'); // Reset animation

                // Mostrar solo los que coinciden con el filtro
                if (filter === 'all' || item.getAttribute('data-category') === filter) {
                    // Usamos un pequeño timeout para que la animación de entrada se vea bien
                    setTimeout(() => {
                        item.style.display = 'block';
                        // Forzamos que la animación se reinicie
                        requestAnimationFrame(() => {
                           item.classList.add('visible');
                        });
                    }, 10);
                }
            });
        });
    });

    // --- CONTADOR ANIMADO DE ESTADÍSTICAS ---
    const statNumbers = document.querySelectorAll('.stat-number');

    const animateCounter = (element) => {
        const target = +element.getAttribute('data-target');
        const duration = 2000; // 2 segundos
        const stepTime = 20; // Actualizar cada 20ms
        const totalSteps = duration / stepTime;
        const increment = target / totalSteps;
        let current = 0;

        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                element.innerText = target;
                clearInterval(timer);
            } else {
                element.innerText = Math.ceil(current);
            }
        }, stepTime);
    };

    const counterObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCounter(entry.target);
                observer.unobserve(entry.target); // Animar solo una vez
            }
        });
    }, { threshold: 0.8 });

    statNumbers.forEach(number => {
        counterObserver.observe(number);
    });

});