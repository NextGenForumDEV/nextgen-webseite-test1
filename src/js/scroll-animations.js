document.addEventListener('DOMContentLoaded', () => {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const delay = parseInt(entry.target.dataset.delay || 0);
                setTimeout(() => {
                    entry.target.classList.remove('opacity-0', 'translate-y-8');
                    entry.target.classList.add('opacity-100', 'translate-y-0');
                }, delay);
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.15 });

    // Group elements by their parent row/grid to stagger them automatically
    const groups = new Map();
    document.querySelectorAll('.scroll-animate').forEach((el) => {
        // Add base styles for transition and initial hidden state
        el.classList.add('transition-all', 'duration-1000', 'ease-out', 'opacity-0', 'translate-y-8');

        // Remove opacity-100 and transform-none if they exist
        el.classList.remove('opacity-100', 'translate-y-0');

        const parent = el.parentElement;
        if (!groups.has(parent)) {
            groups.set(parent, []);
        }
        groups.get(parent).push(el);
    });

    groups.forEach((elements) => {
        elements.forEach((el, index) => {
            el.dataset.delay = 300 + (index * 200); // 300ms base delay + 200ms stagger
            observer.observe(el);
        });
    });
});
