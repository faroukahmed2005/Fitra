// Scroll Animation Handler
document.addEventListener('DOMContentLoaded', () => {
    // Header scroll functionality
    const header = document.querySelector('header');
    let lastScroll = 0;
    const scrollThreshold = 200;
    
    // Set initial state
    header.classList.add('initial');

    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;

        // Scrolling down
        if (currentScroll > lastScroll) {
            if (currentScroll > 0 && currentScroll < scrollThreshold) {
                // Just started scrolling down
                header.classList.remove('scrolled', 'initial');
                header.classList.add('hide');
            } else if (currentScroll >= scrollThreshold) {
                // Passed threshold
                header.classList.remove('hide', 'initial');
                header.classList.add('scrolled');
            }
        } 
        // Scrolling up
        else {
            header.classList.remove('hide');
            if (currentScroll > scrollThreshold) {
                header.classList.remove('initial');
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
                header.classList.add('initial');
            }
        }

        lastScroll = currentScroll;
    });

    // Add fade-in class to elements we want to animate
    const elementsToAnimate = [
        '.about',
        '.section',
        '.extra div',
        '.plans .card',
        'main .container .main',
        'main .container .prag'
    ];

    elementsToAnimate.forEach(selector => {
        document.querySelectorAll(selector).forEach(element => {
            element.classList.add('fade-in');
        });
    });

    // Intersection Observer for scroll animations
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, {
        threshold: 0.1
    });

    // Observe all elements with fade-in class
    document.querySelectorAll('.fade-in').forEach(element => {
        observer.observe(element);
    });

    // Stats Counter Animation
    const stats = document.querySelectorAll('.extra div p');
    
    // Store original values
    stats.forEach(stat => {
        stat.setAttribute('data-value', stat.textContent);
    });

    const animateStats = () => {
        stats.forEach(stat => {
            const target = parseInt(stat.getAttribute('data-value'));
            let current = 0;
            const increment = target / 100;
            const updateCount = () => {
                if (current < target) {
                    current += increment;
                    stat.textContent = Math.ceil(current);
                    requestAnimationFrame(updateCount);
                } else {
                    stat.textContent = target;
                }
            };
            updateCount();
        });
    };

    // Create a new observer for stats
    const statsObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateStats();
            }
        });
    }, {
        threshold: 0.5
    });

    // Observe the stats section
    const statsSection = document.querySelector('.extra');
    if (statsSection) {
        statsObserver.observe(statsSection);
    }

    // Smooth scroll for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add hover effect to cards
    const cards = document.querySelectorAll('.plans .card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
}); 


// === 3D Card Animation ===
document.addEventListener('DOMContentLoaded', function () {
  var container = document.querySelector('.animation-3d-container');
  var card = document.querySelector('.animated-card.animation-3d-card');
  var gokuImg = document.querySelector('.animation-3d-img');

  if (!container || !card || !gokuImg) return;

  container.addEventListener('mousemove', function (e) {
    let bounds = container.getBoundingClientRect();
    let xAxis = (bounds.width / 2 - (e.clientX - bounds.left)) / 15; // حساسية أعلى
    let yAxis = (bounds.height / 2 - (e.clientY - bounds.top)) / 15; // حساسية أعلى
    card.style.transform = `rotateY(${xAxis}deg) rotateX(${yAxis}deg)`;
  });

  container.addEventListener('mouseenter', function () {
    card.classList.add('has-transform');
    gokuImg.classList.add('has-transform');
  });

  container.addEventListener('mouseleave', function () {
    card.style.transform = `rotateY(0deg) rotateX(0deg)`;
    card.classList.remove('has-transform');
    gokuImg.classList.remove('has-transform');
  });
}); 