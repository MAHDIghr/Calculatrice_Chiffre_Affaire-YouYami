(function() {
    'use strict';

    // ============================================
    // CONFIGURATION
    // ============================================
    const CONFIG = {
        animationDuration: 600,
        scrollOffset: 100,
        counterDuration: 1500,
        threshold: 0.15
    };

    // ============================================
    // ANIMATION AU SCROLL (avec effet de révélation)
    // ============================================
    const animateOnScroll = () => {
        const elements = document.querySelectorAll('.cake-card, .stats-card, .report-section, .table-responsive');
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const el = entry.target;
                    const delay = el.dataset.delay || 0;
                    
                    el.style.opacity = '0';
                    el.style.transform = 'translateY(40px)';
                    el.style.transition = `all ${CONFIG.animationDuration}ms cubic-bezier(0.4, 0, 0.2, 1) ${delay}ms`;
                    
                    setTimeout(() => {
                        el.style.opacity = '1';
                        el.style.transform = 'translateY(0)';
                    }, 50);
                    
                    observer.unobserve(el);
                }
            });
        }, { threshold: CONFIG.threshold, rootMargin: '0px 0px -50px 0px' });
        
        elements.forEach(el => observer.observe(el));
    };

    // ============================================
    // EFFET RIPPLE PREMIUM SUR BOUTONS
    // ============================================
    const addRippleEffect = () => {
        const buttons = document.querySelectorAll('.btn');
        
        buttons.forEach(btn => {
            btn.addEventListener('click', function(e) {
                // Éviter les doublons
                const existingRipple = this.querySelector('.ripple-effect');
                if (existingRipple) existingRipple.remove();
                
                const ripple = document.createElement('span');
                ripple.className = 'ripple-effect';
                const rect = this.getBoundingClientRect();
                const size = Math.max(rect.width, rect.height);
                const x = e.clientX - rect.left - size / 2;
                const y = e.clientY - rect.top - size / 2;
                
                ripple.style.cssText = `
                    position: absolute;
                    width: ${size}px;
                    height: ${size}px;
                    background: radial-gradient(circle, rgba(212, 175, 55, 0.4), rgba(212, 175, 55, 0));
                    border-radius: 50%;
                    top: ${y}px;
                    left: ${x}px;
                    pointer-events: none;
                    transform: scale(0);
                    animation: rippleAnimation 0.7s cubic-bezier(0.4, 0, 0.2, 1);
                `;
                
                this.style.position = 'relative';
                this.style.overflow = 'hidden';
                this.appendChild(ripple);
                
                setTimeout(() => ripple.remove(), 700);
            });
        });
    };

    // Style pour l'animation ripple
    const addRippleStyle = () => {
        if (!document.querySelector('#ripple-style')) {
            const style = document.createElement('style');
            style.id = 'ripple-style';
            style.textContent = `
                @keyframes rippleAnimation {
                    0% {
                        transform: scale(0);
                        opacity: 0.7;
                    }
                    100% {
                        transform: scale(4);
                        opacity: 0;
                    }
                }
            `;
            document.head.appendChild(style);
        }
    };

    // ============================================
    // COMPTEUR ANIMÉ LUXURY
    // ============================================
    const animateNumbers = () => {
        const numberElements = document.querySelectorAll('.stats-card h3, .text-success, .text-danger, .fw-bold');
        
        numberElements.forEach(el => {
            const text = el.innerText;
            const match = text.match(/([\d,.]+)/);
            if (match) {
                const rawValue = match[1].replace(/,/g, '');
                const value = parseFloat(rawValue);
                if (!isNaN(value) && value !== 0) {
                    let animated = false;
                    
                    const observer = new IntersectionObserver((entries) => {
                        entries.forEach(entry => {
                            if (entry.isIntersecting && !animated) {
                                animated = true;
                                let current = 0;
                                const increment = value / 60;
                                const stepTime = CONFIG.counterDuration / 60;
                                const prefix = text.replace(match[1], '');
                                const suffix = text.substring(text.indexOf(match[1]) + match[1].length);
                                
                                const updateNumber = () => {
                                    current += increment;
                                    if (current < value) {
                                        const formattedValue = Math.floor(current).toLocaleString();
                                        el.innerText = prefix + formattedValue + suffix;
                                        setTimeout(updateNumber, stepTime);
                                    } else {
                                        el.innerText = prefix + value.toLocaleString() + suffix;
                                    }
                                };
                                
                                updateNumber();
                                observer.unobserve(entry.target);
                            }
                        });
                    }, { threshold: 0.5 });
                    
                    observer.observe(el);
                }
            }
        });
    };

    // ============================================
    // TOOLTIPS PREMIUM
    // ============================================
    const initTooltips = () => {
        const tooltipElements = document.querySelectorAll('[title], [data-tooltip]');
        
        tooltipElements.forEach(el => {
            const title = el.getAttribute('title') || el.getAttribute('data-tooltip');
            if (title && !el.hasAttribute('data-tooltip-init')) {
                el.setAttribute('data-tooltip-init', 'true');
                el.removeAttribute('title');
                
                let tooltipTimeout;
                let tooltipElement = null;
                
                const showTooltip = (e) => {
                    tooltipTimeout = setTimeout(() => {
                        tooltipElement = document.createElement('div');
                        tooltipElement.className = 'custom-tooltip-luxury';
                        tooltipElement.innerText = title;
                        tooltipElement.style.cssText = `
                            position: fixed;
                            background: linear-gradient(135deg, var(--black), var(--black-light));
                            color: var(--gold);
                            padding: 8px 16px;
                            border-radius: 8px;
                            font-size: 12px;
                            font-weight: 500;
                            z-index: 10000;
                            white-space: nowrap;
                            pointer-events: none;
                            font-family: 'Montserrat', sans-serif;
                            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
                            border-left: 3px solid var(--gold);
                            letter-spacing: 0.5px;
                            backdrop-filter: blur(10px);
                            animation: tooltipFadeIn 0.2s ease;
                        `;
                        document.body.appendChild(tooltipElement);
                        
                        const updatePosition = (event) => {
                            const x = event.clientX + 15;
                            const y = event.clientY - 35;
                            tooltipElement.style.left = x + 'px';
                            tooltipElement.style.top = y + 'px';
                        };
                        
                        updatePosition(e);
                        
                        const mouseMoveHandler = (moveEvent) => updatePosition(moveEvent);
                        document.addEventListener('mousemove', mouseMoveHandler);
                        
                        el.addEventListener('mouseleave', () => {
                            if (tooltipElement) tooltipElement.remove();
                            document.removeEventListener('mousemove', mouseMoveHandler);
                            clearTimeout(tooltipTimeout);
                        }, { once: true });
                    }, 300);
                };
                
                el.addEventListener('mouseenter', showTooltip);
                el.addEventListener('mouseleave', () => clearTimeout(tooltipTimeout));
            }
        });
    };

    // Style pour les tooltips
    const addTooltipStyle = () => {
        if (!document.querySelector('#tooltip-style')) {
            const style = document.createElement('style');
            style.id = 'tooltip-style';
            style.textContent = `
                @keyframes tooltipFadeIn {
                    from {
                        opacity: 0;
                        transform: translateY(-5px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }
            `;
            document.head.appendChild(style);
        }
    };

    // ============================================
    // ANIMATION TABLE ROWS
    // ============================================
    const animateTableRows = () => {
        const tableRows = document.querySelectorAll('.table tbody tr');
        tableRows.forEach((row, index) => {
            row.style.opacity = '0';
            row.style.transform = 'translateX(-20px)';
            row.style.transition = `all 0.3s ease ${index * 0.05}s`;
            
            setTimeout(() => {
                row.style.opacity = '1';
                row.style.transform = 'translateX(0)';
            }, 100);
        });
    };

    // ============================================
    // CONFIRMATION MODAL LUXURY
    // ============================================
    const initCustomConfirm = () => {
        const deleteButtons = document.querySelectorAll('[onclick*="supprimerJournee"], [onclick*="delete"]');
        deleteButtons.forEach(btn => {
            const originalOnclick = btn.getAttribute('onclick');
            if (originalOnclick) {
                btn.removeAttribute('onclick');
                btn.addEventListener('click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    showCustomConfirm(originalOnclick);
                });
            }
        });
    };
    
    const showCustomConfirm = (action) => {
        const modal = document.createElement('div');
        modal.className = 'custom-confirm-modal-luxury';
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.85);
            backdrop-filter: blur(8px);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10001;
            animation: modalFadeIn 0.3s ease;
        `;
        
        modal.innerHTML = `
            <div style="background: linear-gradient(135deg, var(--black) 0%, var(--black-light) 100%); border-radius: 20px; padding: 32px; max-width: 420px; width: 90%; text-align: center; border: 1px solid rgba(212, 175, 55, 0.3); box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5); transform: scale(0.9); animation: modalScaleIn 0.3s ease forwards;">
                <div style="width: 70px; height: 70px; background: linear-gradient(135deg, #8B0000, #5C0000); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 20px;">
                    <i class="fas fa-exclamation-triangle" style="font-size: 32px; color: var(--gold);"></i>
                </div>
                <h3 style="color: var(--gold); margin-bottom: 12px; font-family: 'Cormorant Garamond', serif;">Confirmation</h3>
                <p style="margin-bottom: 28px; color: var(--gray);">Voulez-vous vraiment supprimer cette journée ? Cette action est irréversible.</p>
                <div style="display: flex; gap: 15px; justify-content: center;">
                    <button class="btn btn-secondary" id="cancelConfirm" style="padding: 10px 28px;">Annuler</button>
                    <button class="btn btn-danger" id="confirmAction" style="padding: 10px 28px;">Supprimer</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        const addModalStyles = () => {
            if (!document.querySelector('#modal-style')) {
                const style = document.createElement('style');
                style.id = 'modal-style';
                style.textContent = `
                    @keyframes modalFadeIn {
                        from { opacity: 0; }
                        to { opacity: 1; }
                    }
                    @keyframes modalScaleIn {
                        from { transform: scale(0.9); opacity: 0; }
                        to { transform: scale(1); opacity: 1; }
                    }
                `;
                document.head.appendChild(style);
            }
        };
        addModalStyles();
        
        const closeModal = () => {
            modal.style.animation = 'modalFadeOut 0.2s ease';
            setTimeout(() => modal.remove(), 200);
        };
        
        document.getElementById('cancelConfirm').addEventListener('click', closeModal);
        document.getElementById('confirmAction').addEventListener('click', () => {
            closeModal();
            setTimeout(() => {
                try {
                    eval(action);
                } catch(e) {
                    console.error('Erreur lors de la suppression:', e);
                }
            }, 150);
        });
        
        modal.addEventListener('click', (e) => {
            if (e.target === modal) closeModal();
        });
    };

    // ============================================
    // GLOW EFFECT AU SURVOL
    // ============================================
    const addGlowEffect = () => {
        const cards = document.querySelectorAll('.cake-card, .stats-card, .report-section');
        cards.forEach(card => {
            card.addEventListener('mouseenter', () => {
                card.style.transition = 'all 0.3s ease';
            });
        });
    };

    // ============================================
    // PARALLAX EFFECT SUR LES CARTES
    // ============================================
    const initParallax = () => {
        const cards = document.querySelectorAll('.cake-card');
        cards.forEach(card => {
            card.addEventListener('mousemove', (e) => {
                const rect = card.getBoundingClientRect();
                const x = (e.clientX - rect.left) / rect.width - 0.5;
                const y = (e.clientY - rect.top) / rect.height - 0.5;
                const img = card.querySelector('.card-img-top');
                if (img) {
                    img.style.transform = `scale(1.05) translate(${x * 5}px, ${y * 5}px)`;
                }
            });
            card.addEventListener('mouseleave', () => {
                const img = card.querySelector('.card-img-top');
                if (img) {
                    img.style.transform = 'scale(1) translate(0, 0)';
                }
            });
        });
    };

    // ============================================
    // HEADER SCROLL EFFECT
    // ============================================
    const initHeaderScroll = () => {
        const navbar = document.querySelector('.navbar');
        if (navbar) {
            window.addEventListener('scroll', () => {
                if (window.scrollY > 50) {
                    navbar.style.background = 'rgba(26, 26, 26, 0.98)';
                    navbar.style.backdropFilter = 'blur(15px)';
                } else {
                    navbar.style.background = 'rgba(26, 26, 26, 0.95)';
                    navbar.style.backdropFilter = 'blur(12px)';
                }
            });
        }
    };

    // ============================================
    // BACKGROUND PARTICLES EFFECT (OPTIONNEL)
    // ============================================
    const initParticles = () => {
        // Petit effet de particules subtil pour le fond
        const body = document.body;
        for (let i = 0; i < 30; i++) {
            const particle = document.createElement('div');
            particle.className = 'younyami-particle';
            particle.style.cssText = `
                position: fixed;
                width: ${Math.random() * 3}px;
                height: ${Math.random() * 3}px;
                background: radial-gradient(circle, var(--gold), transparent);
                border-radius: 50%;
                left: ${Math.random() * 100}%;
                top: ${Math.random() * 100}%;
                opacity: ${Math.random() * 0.3};
                pointer-events: none;
                z-index: 0;
                animation: floatParticle ${15 + Math.random() * 20}s linear infinite;
            `;
            body.appendChild(particle);
        }
        
        if (!document.querySelector('#particle-style')) {
            const style = document.createElement('style');
            style.id = 'particle-style';
            style.textContent = `
                @keyframes floatParticle {
                    0% {
                        transform: translateY(0) translateX(0);
                        opacity: 0;
                    }
                    10% {
                        opacity: ${Math.random() * 0.3};
                    }
                    90% {
                        opacity: ${Math.random() * 0.2};
                    }
                    100% {
                        transform: translateY(-100vh) translateX(${Math.random() * 100 - 50}px);
                        opacity: 0;
                    }
                }
            `;
            document.head.appendChild(style);
        }
    };

    // ============================================
    // INITIALISATION
    // ============================================
    document.addEventListener('DOMContentLoaded', () => {
        // Ajout des styles nécessaires
        addRippleStyle();
        addTooltipStyle();
        
        // Initialisation des animations
        animateOnScroll();
        addRippleEffect();
        animateNumbers();
        initTooltips();
        animateTableRows();
        initCustomConfirm();
        addGlowEffect();
        initParallax();
        initHeaderScroll();
        
        // Optionnel: désactiver particles si performances
        // initParticles();
        
        // Ajout de la classe pour indiquer le chargement
        document.body.classList.add('calculator-loaded');
        
        // Animation d'entrée pour le conteneur principal
        const mainContainer = document.querySelector('.container');
        if (mainContainer) {
            mainContainer.style.opacity = '0';
            mainContainer.style.transform = 'translateY(20px)';
            setTimeout(() => {
                mainContainer.style.transition = 'all 0.6s ease';
                mainContainer.style.opacity = '1';
                mainContainer.style.transform = 'translateY(0)';
            }, 100);
        }
    });
    
    // ============================================
    // EXPOSE PUBLIC METHODS
    // ============================================
    window.YounYamiCalculator = {
        refreshEffects: () => {
            animateTableRows();
            addRippleEffect();
            animateNumbers();
        },
        showNotification: (message, type = 'success') => {
            const notification = document.createElement('div');
            notification.className = `younyami-notification ${type}`;
            notification.style.cssText = `
                position: fixed;
                bottom: 30px;
                right: 30px;
                background: linear-gradient(135deg, var(--black), var(--black-light));
                color: var(--gold);
                padding: 12px 24px;
                border-radius: 12px;
                border-left: 4px solid ${type === 'success' ? 'var(--gold)' : 'var(--red-light)'};
                box-shadow: 0 10px 25px rgba(0,0,0,0.2);
                z-index: 10002;
                animation: slideInRight 0.3s ease;
                font-family: 'Montserrat', sans-serif;
                font-size: 14px;
            `;
            notification.innerText = message;
            document.body.appendChild(notification);
            setTimeout(() => {
                notification.style.animation = 'slideOutRight 0.3s ease';
                setTimeout(() => notification.remove(), 300);
            }, 3000);
        }
    };
    
    // Styles pour les notifications
    if (!document.querySelector('#notification-style')) {
        const style = document.createElement('style');
        style.id = 'notification-style';
        style.textContent = `
            @keyframes slideInRight {
                from {
                    transform: translateX(100px);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            @keyframes slideOutRight {
                from {
                    transform: translateX(0);
                    opacity: 1;
                }
                to {
                    transform: translateX(100px);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }
    
})();