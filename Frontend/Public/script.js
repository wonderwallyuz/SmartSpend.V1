
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
      if (collapseBtn && sidebar) {
        collapseBtn.addEventListener('click', function (e) {
          e.preventDefault();
          if (!isMobile()) {
            sidebar.classList.toggle('collapsed');
            const pressed = sidebar.classList.contains('collapsed');
            collapseBtn.setAttribute('aria-pressed', String(pressed));
            collapseBtn.innerHTML = pressed
              ? '<i class="fas fa-chevron-right"></i>'
              : '<i class="fas fa-chevron-left"></i>';
          } else {
            sidebar.classList.toggle('show');
          }
        });
      }

      if (toggleBtn && sidebar) {
        toggleBtn.addEventListener('click', function (e) {
          e.stopPropagation();
          sidebar.classList.toggle('show');
        });
      }
      document.addEventListener('click', function (e) {
        if (isMobile() && sidebar && sidebar.classList.contains('show')) {
          const clickedInside = sidebar.contains(e.target) || (toggleBtn && toggleBtn.contains(e.target));
          if (!clickedInside) {
            sidebar.classList.remove('show');
          }
        }
      });

      window.addEventListener('resize', function () {
        if (window.innerWidth > 768) {
          if (sidebar && sidebar.classList.contains('show')) sidebar.classList.remove('show');
        }
      });
    } catch (err) {
      console.error('Sidebar init error:', err);
    }
    function setActiveMenu(item) {
      menuItems.forEach(i => i.classList.remove('active'));
      if (item) item.classList.add('active');
    }

    function showSectionByName(name) {
      if (!name) return;
      const targetId = `${name}Section`;
      const target = document.getElementById(targetId);
      if (target) {
        const all = document.querySelectorAll('[id$="Section"], [data-section]');
        all.forEach(s => {
          if (s.id === targetId) s.style.display = 'block';
          else s.style.display = 'none';
        });
        const titleEl = document.querySelector('.page-title');
        if (titleEl) {
          const nice = name.charAt(0).toUpperCase() + name.slice(1);
          titleEl.textContent = nice;
        }
      } else {
        const titleEl = document.querySelector('.page-title');
        if (titleEl) {
          const nice = name.charAt(0).toUpperCase() + name.slice(1);
          titleEl.textContent = nice;
        }
      }
    }

    // make function available if HTML uses inline onclick="showSection('uploadSection')"
    window.showSection = function (idOrName) {
      // allow call with either 'uploadSection' or 'upload'
      if (!idOrName) return;
      if (idOrName.endsWith('Section')) {
        const el = document.getElementById(idOrName);
        if (el) {
          // show that and hide others
          const all = document.querySelectorAll('[id$="Section"], [data-section]');
          all.forEach(s => {
            s.style.display = (s.id === idOrName) ? 'block' : 'none';
          });
        }
      } else {
        showSectionByName(idOrName);
      }
    };

    try {
      menuItems.forEach(item => {
        item.addEventListener('click', function (e) {
          // allow anchor href but prevent jumping page
          e.preventDefault();
          setActiveMenu(item);

          const name = item.dataset.name;
          if (name) {
            showSectionByName(name);
          }

          // close mobile sidebar after clicking a menu item
          if (isMobile() && sidebar && sidebar.classList.contains('show')) {
            sidebar.classList.remove('show');
          }
        });
      });
    } catch (err) {
      console.error('Menu init error:', err);
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
          // position logic can be added if needed; this just toggles visibility
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
