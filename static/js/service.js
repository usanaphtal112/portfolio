document.addEventListener('DOMContentLoaded', function() {
    const services = document.querySelectorAll('.service');

    services.forEach(service => {
        service.addEventListener('mouseover', () => {
            service.classList.add('hover');
        });

        service.addEventListener('mouseout', () => {
            service.classList.remove('hover');
        });
    });
});
