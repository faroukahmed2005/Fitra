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

function setupComparison(container) {
  const imgAfterContainer = container.querySelector('.img-after-container');
  const handle = container.querySelector('.divider-handle');
  let isDragging = false;
  let autoAnimPlayed = false;

  // أضيف الدايرة جوا الهاندل
  const circle = document.createElement('div');
  circle.classList.add('handle-circle');
  handle.appendChild(circle);

  const startDrag = e => {
    isDragging = true;
    onDrag(e); // أول ما يضغط يتحرك مباشرة
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
    document.removeEventListener('mousemove', onDrag);
    document.removeEventListener('mouseup', endDrag);
    document.removeEventListener('touchmove', onDrag);
    document.removeEventListener('touchend', endDrag);
  };

  // ✅ اسحب من أي مكان في الكونتينر
  container.addEventListener('mousedown', startDrag);
  container.addEventListener('touchstart', startDrag);

  // ===============================
  // ✅ أنيميشن أول ما السكشن يظهر
  // ===============================
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting && !autoAnimPlayed) {
        autoAnimPlayed = true;
        playAutoAnimation();
      }
    });
  }, { threshold: 0.5 });

  observer.observe(container);

  function playAutoAnimation() {
    const rect = container.getBoundingClientRect();
    let positions = [0.5, 0.95, 0.05, 0.5]; // نص → يمين → شمال → نص
    let i = 0;

    function animate() {
      if (i >= positions.length) {
        // 🟢 بعد آخر حركة: شيل الـ transition علشان السحب يبقى سلس
        imgAfterContainer.style.transition = "none";
        handle.style.transition = "none";
        return;
      }

      let percent = positions[i] * 100;

      imgAfterContainer.style.transition = "width 1.5s ease-in-out";
      handle.style.transition = "left 1.5s ease-in-out";

      imgAfterContainer.style.width = percent + '%';
      handle.style.left = (rect.width * positions[i]) - (handle.offsetWidth / 2) + 'px';

      i++;
      setTimeout(animate, 1600); // بعد كل حركة
    }

    animate();
  }
}

// DRAG
document.querySelectorAll('.story-photo-comparison img').forEach(img => {
  img.setAttribute('draggable', 'false');
});










// Successful Stories Carousel Function - تبديل التحولات
document.addEventListener("DOMContentLoaded", () => {
  const container = document.querySelector(".stories-container");
  let cards = Array.from(container.querySelectorAll(".story-transformation-card"));
  const nextBtn = document.getElementById("next-btn");
  const prevBtn = document.getElementById("prev-btn");

  let isAnimating = false;
  const duration = 600; // لازم تبقى نفس اللي في CSS transition

  function showNext() {
    if (isAnimating) return;
    isAnimating = true;

    cards.forEach(card => {
      card.style.transition = `transform ${duration}ms ease`;
      card.style.transform = "translateX(-110%)";
    });

    const oldCard = cards[0];
    oldCard.classList.add("fade-out-left");

    setTimeout(() => {
      cards.forEach(card => {
        card.style.transition = "none";
        card.style.transform = "translateX(0)";
      });

      oldCard.classList.remove("fade-out-left");
      container.appendChild(oldCard);

      cards = Array.from(container.querySelectorAll(".story-transformation-card"));

      const newCard = cards[cards.length - 1];
      newCard.classList.add("fade-in-right");
      setTimeout(() => newCard.classList.remove("fade-in-right"), duration);

      isAnimating = false;
    }, duration);
  }

  function showPrev() {
    if (isAnimating) return;
    isAnimating = true;

    cards.forEach(card => {
      card.style.transition = `transform ${duration}ms ease`;
      card.style.transform = "translateX(110%)";
    });

    const oldCard = cards[cards.length - 1];
    oldCard.classList.add("fade-out-right");

    setTimeout(() => {
      cards.forEach(card => {
        card.style.transition = "none";
        card.style.transform = "translateX(0)";
      });

      oldCard.classList.remove("fade-out-right");
      container.insertBefore(oldCard, cards[0]);

      cards = Array.from(container.querySelectorAll(".story-transformation-card"));

      const newCard = cards[0];
      newCard.classList.add("fade-in-left");
      setTimeout(() => newCard.classList.remove("fade-in-left"), duration);

      isAnimating = false;
    }, duration);
  }

  nextBtn.addEventListener("click", showNext);
  prevBtn.addEventListener("click", showPrev);

  // ------------------------
  // دعم اللمس (Swipe) من 1200px فقط
  // ------------------------
  let startX = 0;
  let endX = 0;

  container.addEventListener("touchstart", (e) => {
    if (window.innerWidth >= 1200) {
      startX = e.touches[0].clientX;
    }
  });

  container.addEventListener("touchend", (e) => {
    if (window.innerWidth >= 1200) {
      endX = e.changedTouches[0].clientX;
      const diff = endX - startX;

      if (Math.abs(diff) > 50) { // لازم يكون السحب واضح (50px)
        if (diff > 0) {
          // Swipe Right = Prev (زي زرار الشمال)
          showPrev();
        } else {
          // Swipe Left = Next (زي زرار اليمين)
          showNext();
        }
      }
    }
  });
});
