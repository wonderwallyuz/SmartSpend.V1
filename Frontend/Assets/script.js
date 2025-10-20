
(function () {
  if (window.__SMARTSPEND_INIT) return;
  window.__SMARTSPEND_INIT = true;

  document.addEventListener('DOMContentLoaded', function () {
    const sidebar = document.getElementById('sidebar');
    const collapseBtn = document.getElementById('collapseBtn');
    const toggleBtn = document.getElementById('toggleSidebarBtn');
    const menuItems = document.querySelectorAll('.menu-item');
    const userProfile = document.getElementById('userProfile');
    const profileMenu = document.getElementById('profileMenu');

    const isMobile = () => window.innerWidth <= 768;
   try {
  const sidebar = document.getElementById('sidebar');
  const toggleBtn = document.getElementById('toggleSidebarBtn');
  const menuItems = document.querySelectorAll('.menu-item');
  const isMobile = () => window.innerWidth <= 768;

  // ✅ Mobile toggle button
  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener('click', function (e) {
      e.stopPropagation();
      sidebar.classList.toggle('show');
    });
  }

  // ✅ Hide sidebar when clicking outside (mobile)
  document.addEventListener('click', function (e) {
    if (isMobile() && sidebar && sidebar.classList.contains('show')) {
      const clickedInside =
        sidebar.contains(e.target) || (toggleBtn && toggleBtn.contains(e.target));
      if (!clickedInside) sidebar.classList.remove('show');
    }
  });

  // ✅ Remove .show when resizing to desktop
  window.addEventListener('resize', function () {
    if (window.innerWidth > 768 && sidebar.classList.contains('show')) {
      sidebar.classList.remove('show');
    }
  });

  // ✅ Highlight active menu item
  function setActiveMenu(item) {
    menuItems.forEach(i => i.classList.remove('active'));
    if (item) item.classList.add('active');
  }

  // ✅ Show specific section by name (if single-page setup)
  function showSectionByName(name) {
    const allSections = document.querySelectorAll('[id$="Section"], [data-section]');
    if (allSections.length === 0) return; // skip if using full Flask pages

    const targetId = document.getElementById(`${name}Section`)
      ? `${name}Section`
      : name;
    const target = document.getElementById(targetId);

    allSections.forEach(s => {
      s.style.display = s === target ? 'block' : 'none';
    });

    const titleEl = document.querySelector('.page-title');
    if (titleEl) {
      const nice = name.charAt(0).toUpperCase() + name.slice(1);
      titleEl.textContent = nice;
    }
  }

  // ✅ Expose globally (for inline use)
  window.showSection = function (idOrName) {
    if (!idOrName) return;
    if (idOrName.endsWith('Section')) {
      const el = document.getElementById(idOrName);
      if (el) {
        const all = document.querySelectorAll('[id$="Section"], [data-section]');
        all.forEach(s => {
          s.style.display = s === el ? 'block' : 'none';
        });
      }
    } else {
      showSectionByName(idOrName);
    }
  };

  // ✅ Menu click behavior
  menuItems.forEach(item => {
    item.addEventListener('click', function (e) {
      const link = item.querySelector('a');
      const href = link ? link.getAttribute('href') : '#';
      const name = item.dataset.name;

      // If href starts with "/" (Flask route), go to page
      if (href.startsWith('/')) return; // allow Flask navigation

      e.preventDefault();
      setActiveMenu(item);
      if (name) showSectionByName(name);
      if (isMobile() && sidebar && sidebar.classList.contains('show')) {
        sidebar.classList.remove('show');
      }
    });
  });

  // ✅ Always show dashboard on load (if section exists)
  const dashboardSection = document.getElementById('dashboardSection');
  if (dashboardSection) {
    showSectionByName('dashboard');
  }

} catch (err) {
  console.error('Sidebar init error:', err);
}

    /* --------------------
       PROFILE DROPDOWN
    -------------------- */
    try {
    if (userProfile && profileMenu) {
  userProfile.addEventListener('click', function (e) {
    e.stopPropagation();
    const open = profileMenu.classList.toggle('show');
    userProfile.setAttribute('aria-expanded', String(open));
    profileMenu.setAttribute('aria-hidden', String(!open));
  });

  // keyboard accessibility
  userProfile.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      userProfile.click();
    }
  });

  // close when clicking outside
  document.addEventListener('click', function (e) {
    if (!userProfile.contains(e.target) && !profileMenu.contains(e.target)) {
      profileMenu.classList.remove('show');
      userProfile.setAttribute('aria-expanded', 'false');
      profileMenu.setAttribute('aria-hidden', 'true');
    }
  });
}
    } catch (err) {
      console.error('Profile menu init error:', err);
    }

    /* --------------------
       CHART (only if present)
    -------------------- */
    try {
      const canvas = document.getElementById('expenseChart');
      if (canvas && typeof Chart !== 'undefined') {
        // destroy existing instance if present
        if (window._expenseChart instanceof Chart) {
          try { window._expenseChart.destroy(); } catch (e) { /* ignore */ }
        }
        const ctx = canvas.getContext('2d');
        window._expenseChart = new Chart(ctx, {
          type: 'pie',
          data: {
            labels: ['Food', 'Transport', 'School', 'Drinks'],
            datasets: [{
              data: [30, 20, 15, 35],
              backgroundColor: ['#FF6B6B', '#4ECDC4', '#FFD93D', '#6A5ACD'],
              borderWidth: 0,
              hoverOffset: 18
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                position: 'top',
                labels: {
                  color: '#fff',
                  usePointStyle: true,
                  pointStyle: 'circle',
                  padding: 20,
                  font: { family: 'Poppins', size: 13 }
                }
              },
              tooltip: {
                bodyColor: '#111',
                backgroundColor: '#fff'
              }
            }
          }
        });
      }
    } catch (err) {
      console.error('Chart setup error:', err);
    }

    

    /* ---------- debugging hint (remove after testing) ---------- */
    // console.log('SmartSpend UI initialized');
  }); // DOMContentLoaded
})(); // IIFE
