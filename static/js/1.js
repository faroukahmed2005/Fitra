// Wait for DOM to be fully loaded
document.addEventListener("DOMContentLoaded", function() {
    // Elements
    const adElement = document.getElementById("ad");
    const overlayElement = document.getElementById("overlay");
    const closeBtnElement = document.getElementById("close-btn");
    
    // Successful Stories Carousel
    initStoriesCarousel();

    // Only show ad if the elements exist
    if (adElement && overlayElement) {
        setTimeout(function () {
            adElement.style.display = "block";
            overlayElement.style.display = "block";
        }, 5000);
    }

    // Only add click listener if close button exists
    if (closeBtnElement) {
        closeBtnElement.addEventListener("click", function (event) {
            event.stopPropagation();
            if (adElement) adElement.style.display = "none";
            if (overlayElement) overlayElement.style.display = "none";
        });
    }

    // Mobile Menu Toggle
    const toggleMenu = document.querySelector('.toggle-menu');
    const navMenu = document.querySelector('header nav ul');
    
    if (toggleMenu && navMenu) {
        toggleMenu.addEventListener('click', function(e) {
            e.preventDefault();
            navMenu.classList.toggle('show-menu');
        });

        // Close menu when clicking on a link
        const menuLinks = navMenu.querySelectorAll('a');
        menuLinks.forEach(link => {
            link.addEventListener('click', function() {
                navMenu.classList.remove('show-menu');
            });
        });

        // Close menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!toggleMenu.contains(e.target) && !navMenu.contains(e.target)) {
                navMenu.classList.remove('show-menu');
            }
        });
    }
});

// Mobile Menu Toggle - Accessible 3 شرط
document.addEventListener("DOMContentLoaded", () => {
  const toggleBtn = document.querySelector(".toggle-menu"); // الأيقونة
  const navMenu = document.querySelector("header nav ul"); // القائمة

  // نخلي الأيقونة زرار Accessible
  toggleBtn.setAttribute("role", "button");
  toggleBtn.setAttribute("tabindex", "0");
  toggleBtn.setAttribute("aria-label", "Toggle menu");

  function toggleMenu() {
    navMenu.classList.toggle("show-menu");
  }

  toggleBtn.addEventListener("click", toggleMenu);

  // عشان كمان لو ضغط Enter من الكيبورد تشتغل
  toggleBtn.addEventListener("keydown", (e) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      toggleMenu();
    }
  });
});





// Glowing Background
const canvas = document.getElementById("glow-bg");
const ctx = canvas.getContext("2d");

function resize() {
  canvas.width = canvas.offsetWidth;
  canvas.height = canvas.offsetHeight;
}
resize();
window.addEventListener("resize", resize);

const blobs = [];
for (let i = 0; i < 15; i++) {
  blobs.push({
    x: Math.random() * canvas.width,
    y: Math.random() * canvas.height,
    r: Math.random() * 60 + 30,
    dx: (Math.random() - 0.5) * 0.3, // حركة أفقية أساسية
    dy: (Math.random() - 0.5) * 0.1  // حركة رأسية خفيفة جدا
  });
}

function drawBackground() {
  const gradient = ctx.createRadialGradient(
    canvas.width/2, canvas.height/2, 50,
    canvas.width/2, canvas.height/2, canvas.width
  );
  gradient.addColorStop(0, "rgba(0,255,100,0.15)");
  gradient.addColorStop(1, "rgba(0,50,0,0.9)");
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, canvas.width, canvas.height);
}

function drawBlobs() {
  blobs.forEach(b => {
    // جسم الكرة
    const g = ctx.createRadialGradient(b.x, b.y, b.r * 0.2, b.x, b.y, b.r);
    g.addColorStop(0, "rgba(0,255,150,0.9)");
    g.addColorStop(0.7, "rgba(0,200,100,0.6)");
    g.addColorStop(1, "rgba(0,100,50,0.15)");

    ctx.beginPath();
    ctx.arc(b.x, b.y, b.r, 0, Math.PI * 2);
    ctx.fillStyle = g;
    ctx.fill();

    // لمعة أخف
    const shine = ctx.createRadialGradient(
      b.x - b.r/3, b.y - b.r/3, 2,
      b.x - b.r/3, b.y - b.r/3, b.r/2
    );
    shine.addColorStop(0, "rgba(255,255,255,0.4)"); // أخف بكتير
    shine.addColorStop(1, "rgba(255,255,255,0)");

    ctx.beginPath();
    ctx.arc(b.x - b.r/3, b.y - b.r/3, b.r/3, 0, Math.PI * 2);
    ctx.fillStyle = shine;
    ctx.fill();

    // حركة
    b.x += b.dx;
    b.y += b.dy;

    // ارتداد أفقي مع مساحة بسيطة عمودي
    if (b.x - b.r < 0 || b.x + b.r > canvas.width) b.dx *= -1;
    if (b.y - b.r < 0 || b.y + b.r > canvas.height) b.dy *= -1;
  });
}

function animate() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  drawBackground();
  drawBlobs();
  requestAnimationFrame(animate);
}
animate();









// Divider-handle 
document.querySelectorAll('.story-photo-comparison').forEach(setupComparison);

// 🛑 علامة عالمية (Global Flag) لضمان تشغيل أنيميشن الـ Divider مرة واحدة فقط.
let hasCarouselAutoAnimPlayed = false;
const carouselSelector = '.stories-carousel';

function setupComparison(container) {
    const imgAfterContainer = container.querySelector('.img-after-container');
    const handle = container.querySelector('.divider-handle');
    let isDragging = false;
    
    // أضيف الدايرة جوا الهاندل
    const circle = document.createElement('div');
    circle.classList.add('handle-circle');
    handle.appendChild(circle);

    const startDrag = e => {
        // *******************************************************
        // 🔴 التعديل الجوهري: منع انتقال الحدث إلى الـ Owl Carousel
        // *******************************************************
        // هذا يضمن أن سحب الـ handle لا يُعتبر سحبًا للـ card.
        e.stopPropagation(); 
        
        isDragging = true;
        
        // 💡 إيقاف الـ Owl Carousel مؤقتاً عند بداية السحب
        $(carouselSelector).trigger('stop.owl.autoplay'); 
        
        onDrag(e); 
        document.addEventListener('mousemove', onDrag);
        document.addEventListener('mouseup', endDrag);
        document.addEventListener('touchmove', onDrag);
        document.addEventListener('touchend', endDrag);
    };

    const onDrag = e => {
        if (!isDragging) return;

        const rect = container.getBoundingClientRect();
        const clientX = e.touches ? e.touches[0].clientX : e.clientX;
        let offsetX = clientX - rect.left;

        if (offsetX < 0) offsetX = 0;
        if (offsetX > rect.width) offsetX = rect.width;

        const percent = (offsetX / rect.width) * 100;
        imgAfterContainer.style.width = percent + '%';
        handle.style.left = offsetX - (handle.offsetWidth / 2) + 'px';
    };

    const endDrag = () => {
        isDragging = false;
        
        // 💡 إعادة تشغيل الـ AutoPlay للـ Owl Carousel
        const owl = $(carouselSelector).data('owl.carousel');
        if (owl && owl.options.autoplay) {
             $(carouselSelector).trigger('play.owl.autoplay');
        }

        document.removeEventListener('mousemove', onDrag);
        document.removeEventListener('mouseup', endDrag);
        document.removeEventListener('touchmove', onDrag);
        document.removeEventListener('touchend', endDrag);
    };

    // ✅ ربط السحب بالـ Handle فقط (لتنفيذ طلبك)
    handle.addEventListener('mousedown', startDrag);
    handle.addEventListener('touchstart', startDrag);


    // ===============================
    // ✅ أنيميشن أول ما السكشن يظهر 
    // ===============================
    
    // نشغل الـ Observer على أول كارت فقط
    const isFirstComparison = container === document.querySelector('.story-photo-comparison');

    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !hasCarouselAutoAnimPlayed) {
                hasCarouselAutoAnimPlayed = true; 
                
                document.querySelectorAll('.story-photo-comparison').forEach(comp => {
                    playAutoAnimation(comp, comp === container); 
                });

                observer.unobserve(container);
            }
        });
    }, { threshold: 0.2 });

    if (isFirstComparison) {
        observer.observe(container);
    }


    function playAutoAnimation(comparisonElement, shouldStartAutoPlay) {
        const afterContainer = comparisonElement.querySelector('.img-after-container');
        const handle = comparisonElement.querySelector('.divider-handle');
        const rect = comparisonElement.getBoundingClientRect();
        
        let positions = [0.5, 0.95, 0.05, 0.5]; 
        let i = 0;
        const duration = 1500;
        const delay = 1600;

        function startCarouselAutoPlay() {
             const owl = $(carouselSelector).data('owl.carousel');
             if (owl) {
                 // تفعيل خيار الأوتو بلاي في إعدادات الـ Owl Carousel
                 owl.settings.autoplay = true; 
                 owl.options.autoplay = true; 
                 $(carouselSelector).trigger('play.owl.autoplay', [5000]); // تشغيل الأوتو بلاي بمدة 5 ثواني
             }
        }
        
        function animate() {
            if (i >= positions.length) {
                // بعد آخر حركة: شيل الـ transition علشان السحب يبقى سلس
                afterContainer.style.transition = "none";
                handle.style.transition = "none";

                if (shouldStartAutoPlay) {
                    startCarouselAutoPlay(); 
                }
                
                return;
            }

            let percent = positions[i] * 100;

            afterContainer.style.transition = `width ${duration / 1000}s ease-in-out`;
            handle.style.transition = `left ${duration / 1000}s ease-in-out`;

            afterContainer.style.width = percent + '%';
            handle.style.left = (rect.width * positions[i]) - (handle.offsetWidth / 2) + 'px';

            i++;
            setTimeout(animate, delay);
        }

        animate();
    }
}

// DRAG (لتحديد خاصية عدم السحب للصور)
document.querySelectorAll('.story-photo-comparison img').forEach(img => {
  img.setAttribute('draggable', 'false');
});
