/* Sidebar collapse / toggle */
const sidebar = document.getElementById("sidebar");
const collapseBtn = document.getElementById("collapseBtn");

collapseBtn.addEventListener("click", () => {
  sidebar.classList.toggle("collapsed");

  const isCollapsed = sidebar.classList.contains("collapsed");
  collapseBtn.setAttribute("aria-pressed", String(isCollapsed));
  collapseBtn.innerHTML = isCollapsed
    ? '<i class="fas fa-chevron-right"></i>'
    : '<i class="fas fa-chevron-left"></i>';
});

// Mobile toggle (optional: tap avatar to open sidebar)
document.querySelector(".avatar").addEventListener("click", () => {
  sidebar.classList.toggle("show");
});


toggleSidebarBtn?.addEventListener("click", () => {
  // Toggle collapse for a quick hide/show
  sidebar.classList.toggle("collapsed");
});

/* Menu activation (adds 'active' class to clicked item) */
document.querySelectorAll(".menu-item").forEach(item => {
  item.addEventListener("click", (e) => {
    // prevent default anchor behavior
    e.preventDefault();

    document.querySelectorAll(".menu-item").forEach(i => i.classList.remove("active"));
    item.classList.add("active");
  });
});

/* Profile menu show/hide */
const userProfile = document.getElementById("userProfile");
const profileMenu = document.getElementById("profileMenu");

function toggleProfileMenu() {
  const isOpen = profileMenu.style.display === "block";
  if (isOpen) {
    profileMenu.style.display = "none";
    userProfile.setAttribute("aria-expanded", "false");
    profileMenu.setAttribute("aria-hidden", "true");
  } else {
    profileMenu.style.display = "block";
    userProfile.setAttribute("aria-expanded", "true");
    profileMenu.setAttribute("aria-hidden", "false");
  }
}

userProfile?.addEventListener("click", (e) => {
  e.stopPropagation();
  toggleProfileMenu();
});

/* close profile when clicking outside */
document.addEventListener("click", (e) => {
  const isClickInside = userProfile?.contains(e.target) || profileMenu?.contains(e.target);
  if (!isClickInside) {
    profileMenu.style.display = "none";
    userProfile?.setAttribute("aria-expanded", "false");
    profileMenu?.setAttribute("aria-hidden", "true");
  }
});

/* Chart.js pie chart - responsive and centered */
const ctx = document.getElementById("expenseChart").getContext("2d");

const expenseChart = new Chart(ctx, {
  type: "pie",
  data: {
    labels: ["Food", "Transport", "School", "Drinks"],
    datasets: [{
      data: [30, 20, 15, 35],
      backgroundColor: ["#FF6B6B","#4ECDC4","#FFD93D","#6A5ACD"],
      borderWidth: 0,
      hoverOffset: 18
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins:{
      legend: {
        position: "top",
        labels: {
          color: "#fff",
          usePointStyle: true,
          pointStyle: "circle",
          padding: 20,
          font: { family: "Poppins", size: 13 }
        }
      },
      tooltip: {
        bodyColor: "#111",
        backgroundColor: "#fff"
      }
    },
    animation: { animateRotate: true, animateScale: true }
  }
});

// script.js — safe initialization for dashboard + profile pages
(function(){
  // Prevent double initialization if script is accidentally included twice
  if (window.__SMARTSPEND_INIT) return;
  window.__SMARTSPEND_INIT = true;

  document.addEventListener('DOMContentLoaded', function() {
    // ---------- Chart (only if canvas exists) ----------
    const canvas = document.getElementById('expenseChart');
    if (canvas) {
      try {
        const ctx = canvas.getContext('2d');
        // If a previous chart instance exists, destroy it
        if (window.expenseChart instanceof Chart) {
          window.expenseChart.destroy();
          window.expenseChart = null;
        }
        window.expenseChart = new Chart(ctx, {
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
            },
            animation: { animateRotate: true, animateScale: true }
          }
        });
      } catch (err) {
        console.error('Chart initialization failed:', err);
      }
    }

    // ---------- Sidebar toggle (safe guards) ----------
  const sidebar = document.getElementById("sidebar");
const collapseBtn = document.getElementById("collapseBtn");
const toggleSidebarBtn = document.getElementById("toggleSidebarBtn");

if (collapseBtn && sidebar) {
  collapseBtn.addEventListener("click", () => {
    // Desktop collapse
    if (window.innerWidth > 768) {
      sidebar.classList.toggle("collapsed");
      const pressed = sidebar.classList.contains("collapsed");
      collapseBtn.setAttribute("aria-pressed", String(pressed));
      collapseBtn.innerHTML = pressed
        ? '<i class="fas fa-chevron-right"></i>'
        : '<i class="fas fa-chevron-left"></i>';
    } else {
      // Mobile slide
      sidebar.classList.toggle("show");
    }
  });
}

if (toggleSidebarBtn && sidebar) {
  toggleSidebarBtn.addEventListener("click", () => {
    sidebar.classList.toggle("show");
  });
}

// Close mobile sidebar when clicking outside
document.addEventListener("click", (e) => {
  if (
    window.innerWidth <= 768 &&
    sidebar.classList.contains("show") &&
    !sidebar.contains(e.target) &&
    !collapseBtn.contains(e.target) &&
    !toggleSidebarBtn.contains(e.target)
  ) {
    sidebar.classList.remove("show");
  }
});

    // ---------- Menu activation ----------
    document.querySelectorAll('.menu-item').forEach(item => {
      item.addEventListener('click', () => {
        document.querySelectorAll('.menu-item').forEach(i => i.classList.remove('active'));
        item.classList.add('active');
      });
    });

    // ---------- Profile dropdown (safe guards) ----------
    const userProfile = document.getElementById('userProfile');
    const profileMenu = document.getElementById('profileMenu');

    if (userProfile && profileMenu) {
      userProfile.addEventListener('click', (e) => {
        e.stopPropagation();
        const isShown = profileMenu.classList.toggle('show');
        userProfile.setAttribute('aria-expanded', String(isShown));
        profileMenu.setAttribute('aria-hidden', String(!isShown));
      });

      // Close when clicking outside
      document.addEventListener('click', (e) => {
        if (!userProfile.contains(e.target) && !profileMenu.contains(e.target)) {
          profileMenu.classList.remove('show');
          userProfile.setAttribute('aria-expanded', 'false');
          profileMenu.setAttribute('aria-hidden', 'true');
        }
      });

      // If profile menu contains links, close menu before navigation
      profileMenu.querySelectorAll('a').forEach(a => {
        a.addEventListener('click', () => {
          profileMenu.classList.remove('show');
          userProfile.setAttribute('aria-expanded', 'false');
          profileMenu.setAttribute('aria-hidden', 'true');
        });
      });

      // keyboard accessibility
      userProfile.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          userProfile.click();
        }
      });
    }

    // Optional: add any other small safe initializations here

  }); // end DOMContentLoaded
})(); // end IIFE
// Profile photo upload & preview
const photoInput = document.getElementById("photoInput");
const userPhoto = document.getElementById("userPhoto");

// Load saved profile picture if it exists
window.addEventListener("DOMContentLoaded", () => {
  const savedPic = localStorage.getItem("profilePic");
  if (savedPic && userPhoto) {
    userPhoto.src = savedPic;
  }
});

if (photoInput && userPhoto) {
  photoInput.addEventListener("change", function () {
    const file = this.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = function (e) {
        userPhoto.src = e.target.result; // update profile image
        localStorage.setItem("profilePic", e.target.result); // save to localStorage
      };
      reader.readAsDataURL(file);
    }
  });
}



// ------------- PROFILE DROPDOWN: anchored + fixed positioning -------------
(function () {
  const userProfile = document.getElementById('userProfile');
  const profileMenu = document.getElementById('profileMenu');

  if (!userProfile || !profileMenu) return;

  // helper: position the menu below/right of the avatar
  function positionProfileMenu() {
    const rect = userProfile.getBoundingClientRect();
    const menuRect = profileMenu.getBoundingClientRect();

    // place menu so its right edge matches avatar right edge,
    // and its top is slightly below avatar bottom (8px)
    const left = Math.min(window.innerWidth - menuRect.width - 12, rect.right - menuRect.width + 8);
    const top = rect.bottom + 8;

    profileMenu.style.left = `${Math.max(8, left)}px`;
    profileMenu.style.top = `${Math.max(8, top)}px`;
  }

  // toggle open/close
  userProfile.addEventListener('click', (e) => {
    e.stopPropagation();
    profileMenu.classList.toggle('show');
    if (profileMenu.classList.contains('show')) {
      positionProfileMenu();
    }
  });

  // close when clicking outside
  document.addEventListener('click', (e) => {
    if (!userProfile.contains(e.target) && !profileMenu.contains(e.target)) {
      profileMenu.classList.remove('show');
    }
  });

  // reposition on scroll/resize when open
  window.addEventListener('scroll', () => {
    if (profileMenu.classList.contains('show')) positionProfileMenu();
  }, { passive: true });

  window.addEventListener('resize', () => {
    if (profileMenu.classList.contains('show')) positionProfileMenu();
  });

  // Make sure clicking any link closes the menu (so navigation is smooth)
  profileMenu.querySelectorAll('a').forEach(a => {
    a.addEventListener('click', () => {
      profileMenu.classList.remove('show');
    });
  });

})();

// Add Expense button
const addExpenseBtn = document.getElementById("addExpenseBtn");
const expenseTable = document.getElementById("expenseTable").querySelector("tbody");

addExpenseBtn.addEventListener("click", () => {
  const desc = document.getElementById("desc").value.trim();
  const amount = document.getElementById("amount").value.trim();
  const date = document.getElementById("date").value;
  const category = document.getElementById("category").value;

  if (!desc || !amount || !date) {
    alert("Please fill out all fields.");
    return;
  }

  const row = document.createElement("tr");
  row.innerHTML = `
    <td>${desc}</td>
    <td>₱${amount}</td>
    <td>${date}</td>
    <td>${category}</td>
  `;

  expenseTable.appendChild(row);

  // Clear inputs
  document.getElementById("desc").value = "";
  document.getElementById("amount").value = "";
  document.getElementById("date").value = "";
  document.getElementById("category").selectedIndex = 0;
});

// Upload File clickable
const fileInput = document.getElementById("fileInput");
const uploadBox = document.querySelector(".upload-box");

uploadBox.addEventListener("click", () => {
  fileInput.click();
});

fileInput.addEventListener("change", () => {
  if (fileInput.files.length > 0) {
    alert(`File uploaded: ${fileInput.files[0].name}`);
  }
});

