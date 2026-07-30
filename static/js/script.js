/* =========================================================
   MediPredict AI — script.js
   Handles: symptom search filter, selection counter,
   flash alert auto-dismiss, smooth scrolling.
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    /* ---------------------------------------------------
       1. Searchable Symptom Filter
       Filters the symptom checklist live as the user types,
       so choosing from 55 symptoms stays fast and usable.
    --------------------------------------------------- */
    const searchInput = document.getElementById("symptomSearch");
    const symptomItems = document.querySelectorAll(".symptom-check");

    if (searchInput) {
        searchInput.addEventListener("input", function () {
            const query = this.value.trim().toLowerCase();

            symptomItems.forEach(function (item) {
                const label = item.querySelector("label").textContent.toLowerCase();
                item.style.display = label.includes(query) ? "block" : "none";
            });
        });
    }

    /* ---------------------------------------------------
       2. Live Selected Symptom Counter
       Updates a badge showing how many symptoms are checked,
       and gently warns if fewer than 2 are selected.
    --------------------------------------------------- */
    const symptomCheckboxes = document.querySelectorAll('input[name="symptoms"]');
    const counterBadge = document.getElementById("selectedCount");

    function updateSymptomCount() {
        if (!counterBadge) return;
        const checkedCount = document.querySelectorAll('input[name="symptoms"]:checked').length;
        counterBadge.textContent = checkedCount + " selected";

        if (checkedCount === 0) {
            counterBadge.className = "badge bg-secondary";
        } else if (checkedCount === 1) {
            counterBadge.className = "badge bg-warning text-dark";
        } else {
            counterBadge.className = "badge bg-success";
        }
    }

    if (symptomCheckboxes.length > 0) {
        symptomCheckboxes.forEach(function (checkbox) {
            checkbox.addEventListener("change", updateSymptomCount);
        });
        updateSymptomCount(); // initialize on page load
    }

    /* ---------------------------------------------------
       3. Prediction Form Client-Side Validation,
          Step Progress Indicator, and Loading Overlay
    --------------------------------------------------- */
    const predictForm = document.getElementById("predictForm");
    const step2 = document.getElementById("step2");
    const loadingOverlay = document.getElementById("predictLoadingOverlay");

    // Advance to "Step 2 - Symptoms" visually once the user starts checking symptoms
    if (symptomCheckboxes.length > 0 && step2) {
        symptomCheckboxes.forEach(function (checkbox) {
            checkbox.addEventListener("change", function () {
                const anyChecked = document.querySelectorAll('input[name="symptoms"]:checked').length > 0;
                step2.classList.toggle("active", anyChecked);
            });
        });
    }

    if (predictForm) {
        predictForm.addEventListener("submit", function (event) {
            const checkedCount = document.querySelectorAll('input[name="symptoms"]:checked').length;

            if (!predictForm.checkValidity() || checkedCount === 0) {
                event.preventDefault();
                event.stopPropagation();
                predictForm.classList.add("was-validated");
                return;
            }

            // Valid submission: show the AI "analyzing" loading overlay
            if (loadingOverlay) {
                loadingOverlay.classList.remove("d-none");
            }
            predictForm.classList.add("was-validated");
        });
    }

    /* ---------------------------------------------------
       4. Toast Notifications
       Converts server-side flash messages into slide-in toasts,
       and exposes window.showToast() for JS-triggered messages
       (e.g. loading/prediction feedback).
    --------------------------------------------------- */
    const toastContainer = document.getElementById("toastContainer");

    function showToast(message, type = "warning", icon = "exclamation-triangle-fill") {
        if (!toastContainer) return;
        const toastEl = document.createElement("div");
        toastEl.className = `custom-toast toast-${type}`;
        toastEl.innerHTML = `
            <i class="bi bi-${icon}"></i>
            <span>${message}</span>
            <button class="toast-close" aria-label="Close">&times;</button>
        `;
        toastContainer.appendChild(toastEl);

        const removeToast = () => {
            toastEl.classList.add("toast-hide");
            setTimeout(() => toastEl.remove(), 300);
        };

        toastEl.querySelector(".toast-close").addEventListener("click", removeToast);
        setTimeout(removeToast, 6000);
    }
    window.showToast = showToast; // expose globally for other scripts/pages

    // Convert any server-rendered flash messages into toasts on page load
    const flashMessages = document.querySelectorAll("#flashMessages .flash-message");
    flashMessages.forEach(function (el) {
        showToast(el.textContent, el.dataset.type || "warning");
    });

    /* ---------------------------------------------------
       5. Dark Mode Toggle
       Persists the user's preference in localStorage so it
       survives page reloads and repeat visits.
    --------------------------------------------------- */
    const darkModeToggle = document.getElementById("darkModeToggle");
    const darkModeIcon = document.getElementById("darkModeIcon");
    const THEME_KEY = "medipredict-theme";

    function applyThemeIcon() {
        const isDark = document.documentElement.getAttribute("data-theme") === "dark";
        if (darkModeIcon) {
            darkModeIcon.className = isDark ? "bi bi-sun-fill" : "bi bi-moon-stars-fill";
        }
    }
    applyThemeIcon();

    if (darkModeToggle) {
        darkModeToggle.addEventListener("click", function () {
            const isDark = document.documentElement.getAttribute("data-theme") === "dark";
            if (isDark) {
                document.documentElement.removeAttribute("data-theme");
                localStorage.setItem(THEME_KEY, "light");
            } else {
                document.documentElement.setAttribute("data-theme", "dark");
                localStorage.setItem(THEME_KEY, "dark");
            }
            applyThemeIcon();
        });
    }

    /* ---------------------------------------------------
       7. Animated Stats Counter (Home page hero)
       Counts up from 0 to the target number when it scrolls
       into view, using IntersectionObserver.
    --------------------------------------------------- */
    const counters = document.querySelectorAll(".counter");

    function animateCounter(el) {
        const target = parseInt(el.dataset.count, 10) || 0;
        const suffix = el.dataset.suffix || "";
        const duration = 1200; // ms
        const startTime = performance.now();

        function tick(now) {
            const progress = Math.min((now - startTime) / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
            el.textContent = Math.round(eased * target) + suffix;
            if (progress < 1) {
                requestAnimationFrame(tick);
            }
        }
        requestAnimationFrame(tick);
    }

    if (counters.length > 0 && "IntersectionObserver" in window) {
        const observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    animateCounter(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.5 });

        counters.forEach(function (counter) {
            observer.observe(counter);
        });
    } else {
        // Fallback: just set final values immediately
        counters.forEach(function (el) {
            el.textContent = (el.dataset.count || "0") + (el.dataset.suffix || "");
        });
    }

    /* ---------------------------------------------------
       8. Smooth scroll for in-page anchor links
    --------------------------------------------------- */
    document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
        anchor.addEventListener("click", function (e) {
            const targetId = this.getAttribute("href");
            if (targetId.length > 1) {
                const target = document.querySelector(targetId);
                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({ behavior: "smooth", block: "start" });
                }
            }
        });
    });

});
