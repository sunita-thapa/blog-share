// ============================================================
// main.js — JavaScript for BlogSphere
// All interactive features: forms, animations, cookie banner
// ============================================================

document.addEventListener('DOMContentLoaded', function () {

  // ----------------------------------------------------------
  // 1. AUTO-DISMISS FLASH ALERTS after 5 seconds
  // ----------------------------------------------------------
  const alerts = document.querySelectorAll('.alert.auto-dismiss');
  alerts.forEach(function (alert) {
    setTimeout(function () {
      alert.style.transition = 'opacity 0.6s';
      alert.style.opacity    = '0';
      setTimeout(function () { alert.remove(); }, 600);
    }, 5000);
  });


  // ----------------------------------------------------------
  // 2. CLIENT-SIDE FORM VALIDATION
  // Highlights empty required fields before submitting
  // ----------------------------------------------------------
  const forms = document.querySelectorAll('.needs-validation');
  forms.forEach(function (form) {
    form.addEventListener('submit', function (event) {
      if (!form.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();
      }
      form.classList.add('was-validated');
    }, false);
  });


  // ----------------------------------------------------------
  // 3. PASSWORD STRENGTH METER
  // Shows a coloured bar as the user types their password
  // ----------------------------------------------------------
  const pwInput  = document.getElementById('password');
  const pwMeter  = document.getElementById('password-strength');
  const pwHint   = document.getElementById('password-hint');

  if (pwInput && pwMeter) {
    pwInput.addEventListener('input', function () {
      const val   = pwInput.value;
      let score   = 0;
      let label   = '';
      let colour  = '';

      if (val.length >= 6)  score++;
      if (val.length >= 10) score++;
      if (/[A-Z]/.test(val)) score++;
      if (/[0-9]/.test(val)) score++;
      if (/[^A-Za-z0-9]/.test(val)) score++;

      switch (true) {
        case score <= 1: label = 'Weak';   colour = '#dc143c'; break;
        case score <= 3: label = 'Fair';   colour = '#f59e0b'; break;
        case score <= 4: label = 'Good';   colour = '#0ea5e9'; break;
        default:         label = 'Strong'; colour = '#16a34a'; break;
      }

      pwMeter.style.width      = (score * 20) + '%';
      pwMeter.style.background = colour;
      if (pwHint) { pwHint.textContent = label; pwHint.style.color = colour; }
    });
  }


  // ----------------------------------------------------------
  // 4. CONFIRM BEFORE DELETE
  // Shows a nice custom dialog instead of ugly browser confirm()
  // ----------------------------------------------------------
  const deleteModal = document.getElementById('deleteModal');
  const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
  let deleteForm = null;

  document.querySelectorAll('.delete-trigger').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      deleteForm = btn.closest('form') || document.getElementById(btn.dataset.form);
      const itemName = btn.dataset.name || 'this item';
      const labelEl  = document.getElementById('deleteItemName');
      if (labelEl) labelEl.textContent = itemName;
      if (deleteModal) {
        const modal = new bootstrap.Modal(deleteModal);
        modal.show();
      }
    });
  });

  if (confirmDeleteBtn) {
    confirmDeleteBtn.addEventListener('click', function () {
      if (deleteForm) deleteForm.submit();
    });
  }


  // ----------------------------------------------------------
  // 5. SKILL BAR ANIMATION ON SCROLL
  // Progress bars animate into view when they enter the viewport
  // ----------------------------------------------------------
  const skillBars = document.querySelectorAll('.skill-bar-fill');

  const observerOptions = { threshold: 0.3 };
  const observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        const bar    = entry.target;
        const target = bar.dataset.width || '0';
        bar.style.width = target + '%';
        observer.unobserve(bar);
      }
    });
  }, observerOptions);

  skillBars.forEach(function (bar) {
    bar.style.width = '0';  // Start at 0, animate to target
    observer.observe(bar);
  });


  // ----------------------------------------------------------
  // 6. CHARACTER COUNTER for textareas
  // Shows "120 / 300 characters" below textareas
  // ----------------------------------------------------------
  document.querySelectorAll('textarea[maxlength]').forEach(function (ta) {
    const max     = parseInt(ta.getAttribute('maxlength'));
    const counter = document.createElement('small');
    counter.className = 'text-muted char-counter';
    counter.textContent = `0 / ${max}`;
    ta.parentNode.insertBefore(counter, ta.nextSibling);

    ta.addEventListener('input', function () {
      const len = ta.value.length;
      counter.textContent = `${len} / ${max}`;
      counter.style.color = len > max * 0.9 ? '#dc143c' : '#64748b';
    });
  });


  // ----------------------------------------------------------
  // 7. COOKIE BANNER
  // Shows once, hides permanently after "Accept"
  // ----------------------------------------------------------
  const cookieBanner = document.getElementById('cookieBanner');
  if (cookieBanner) {
    // Only show if user hasn't accepted yet
    if (!localStorage.getItem('cookiesAccepted')) {
      cookieBanner.style.display = 'flex';
    }

    const acceptBtn = document.getElementById('acceptCookies');
    if (acceptBtn) {
      acceptBtn.addEventListener('click', function () {
        localStorage.setItem('cookiesAccepted', 'true');
        cookieBanner.style.opacity = '0';
        setTimeout(function () { cookieBanner.remove(); }, 400);
      });
    }
  }


  // ----------------------------------------------------------
  // 8. SEARCH BOX — live filter on blog page
  // Hides/shows post cards as user types (frontend-only)
  // ----------------------------------------------------------
  const liveSearch = document.getElementById('liveSearch');
  const postCards  = document.querySelectorAll('.post-card-item');

  if (liveSearch && postCards.length) {
    liveSearch.addEventListener('input', function () {
      const q = liveSearch.value.toLowerCase().trim();
      let visible = 0;
      postCards.forEach(function (card) {
        const text = card.textContent.toLowerCase();
        if (!q || text.includes(q)) {
          card.style.display = '';
          visible++;
        } else {
          card.style.display = 'none';
        }
      });
      const noResults = document.getElementById('noResults');
      if (noResults) noResults.style.display = visible ? 'none' : 'block';
    });
  }


  // ----------------------------------------------------------
  // 9. COLOUR BADGE PREVIEW (technology form)
  // Shows a live colour swatch next to the colour input
  // ----------------------------------------------------------
  const colorInput  = document.getElementById('badge_color');
  const colorSwatch = document.getElementById('colorSwatch');

  if (colorInput && colorSwatch) {
    colorSwatch.style.background = colorInput.value;
    colorInput.addEventListener('input', function () {
      colorSwatch.style.background = colorInput.value;
    });
  }


  // ----------------------------------------------------------
  // 10. SMOOTH SCROLL for anchor links
  // ----------------------------------------------------------
  document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
    anchor.addEventListener('click', function (e) {
      const target = document.querySelector(anchor.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });


  // ----------------------------------------------------------
  // 11. ACTIVE NAV LINK highlight based on current URL
  // ----------------------------------------------------------
  const currentPath = window.location.pathname;
  document.querySelectorAll('.nav-link').forEach(function (link) {
    if (link.getAttribute('href') === currentPath) {
      link.classList.add('active');
    }
  });


  // ----------------------------------------------------------
  // 12. SIDEBAR MOBILE TOGGLE (for dashboard on small screens)
  // ----------------------------------------------------------
  const sidebarToggle = document.getElementById('sidebarToggle');
  const sidebar       = document.getElementById('dashboardSidebar');

  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener('click', function () {
      sidebar.classList.toggle('sidebar-open');
    });
  }

});
