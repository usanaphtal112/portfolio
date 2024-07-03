document.addEventListener('DOMContentLoaded', (event) => {
    // Fade-in animation for main content
    const mainContent = document.querySelector('.main-content');
    mainContent.style.opacity = '0';
    mainContent.style.transform = 'translateY(20px)';
    mainContent.style.transition = 'opacity 0.5s ease, transform 0.5s ease';

    setTimeout(() => {
        mainContent.style.opacity = '1';
        mainContent.style.transform = 'translateY(0)';
    }, 200);

    // Pulse animation for primary button
    const primaryButton = document.querySelector('.buttons .primary');
    primaryButton.addEventListener('mouseenter', () => {
        primaryButton.style.animation = 'pulse 0.5s';
    });

    primaryButton.addEventListener('animationend', () => {
        primaryButton.style.animation = '';
    });
});

@keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.05); }
    100% { transform: scale(1); }
}
