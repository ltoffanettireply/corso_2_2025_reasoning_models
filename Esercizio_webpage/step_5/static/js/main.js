// Script principale per Tech Reviews

document.addEventListener('DOMContentLoaded', function() {
    // Animazioni di scroll
    const animateOnScroll = () => {
        const fadeInElements = document.querySelectorAll('.review-card');
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = 1;
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        }, { threshold: 0.1 });
        
        fadeInElements.forEach(element => {
            element.style.opacity = 0;
            element.style.transform = 'translateY(20px)';
            element.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            observer.observe(element);
        });
    };

    // Validazione della newsletter
    const setupNewsletterForm = () => {
        const newsletterForm = document.querySelector('.newsletter-form');
        
        if (newsletterForm) {
            newsletterForm.addEventListener('submit', function(e) {
                e.preventDefault();
                
                const emailInput = this.querySelector('input[type="email"]');
                const email = emailInput.value.trim();
                
                if (!isValidEmail(email)) {
                    showToast('Inserisci un indirizzo email valido');
                    emailInput.focus();
                    return;
                }
                
                // Simula l'invio del form
                showToast('Grazie per l\'iscrizione!');
                emailInput.value = '';
            });
        }
    };
    
    // Funzione di utilità per validare email
    const isValidEmail = (email) => {
        const re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        return re.test(email.toLowerCase());
    };
    
    // Toast notification
    const showToast = (message) => {
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        // Stile per il toast
        toast.style.position = 'fixed';
        toast.style.bottom = '20px';
        toast.style.right = '20px';
        toast.style.padding = '12px 20px';
        toast.style.backgroundColor = 'rgba(52, 152, 219, 0.9)';
        toast.style.color = '#fff';
        toast.style.borderRadius = '4px';
        toast.style.zIndex = '1000';
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(20px)';
        toast.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
        
        // Mostra il toast
        setTimeout(() => {
            toast.style.opacity = '1';
            toast.style.transform = 'translateY(0)';
        }, 10);
        
        // Rimuovi il toast dopo 3 secondi
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                document.body.removeChild(toast);
            }, 300);
        }, 3000);
    };

    // Inizializza le funzioni
    animateOnScroll();
    setupNewsletterForm();
});
