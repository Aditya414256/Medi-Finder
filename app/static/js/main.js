/**
 * MediFind Main Client Scripts
 * Includes Google-like Medicine Autocomplete with Keyboard Navigation
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Auto dismiss alerts after 5 seconds
  const alerts = document.querySelectorAll('.alert');
  alerts.forEach(alert => {
    setTimeout(() => {
      alert.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
      alert.style.opacity = '0';
      alert.style.transform = 'translateY(-10px)';
      setTimeout(() => alert.remove(), 500);
    }, 5000);
  });

  // 2. Geolocation prompt helper for nearby search & sorting
  const geoButtons = document.querySelectorAll('[data-action="get-location"]');
  geoButtons.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      if (!navigator.geolocation) {
        alert("Geolocation is not supported by your browser. You can still browse pharmacies and view store profiles.");
        return;
      }
      const origHtml = btn.innerHTML;
      btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Locating...';
      btn.disabled = true;

      navigator.geolocation.getCurrentPosition(
        (position) => {
          const lat = position.coords.latitude.toFixed(6);
          const lon = position.coords.longitude.toFixed(6);
          sessionStorage.setItem('user_lat', lat);
          sessionStorage.setItem('user_lon', lon);
          
          const currentPath = window.location.pathname;
          // If on home page, navigate to nearby pharmacies list
          if (currentPath === '/' || currentPath === '') {
            window.location.href = `/pharmacies?lat=${lat}&lon=${lon}`;
            return;
          }

          // Otherwise update current view with coordinates
          const targetUrl = new URL(window.location.href);
          targetUrl.searchParams.set('lat', lat);
          targetUrl.searchParams.set('lon', lon);
          window.location.href = targetUrl.toString();
        },
        (error) => {
          btn.innerHTML = origHtml;
          btn.disabled = false;
          let msg = "Location access was not granted. Pharmacies will continue to be displayed. You can still inspect inventory and view pharmacy details.";
          if (error.code === error.PERMISSION_DENIED) {
            msg = "Location permission was denied. Pharmacies are listed by availability. You can enable location in browser settings to calculate exact distances.";
          }
          alert(msg);
        },
        { timeout: 10000, enableHighAccuracy: true }
      );
    });
  });

  // Auto-apply saved session coordinates to medicine and pharmacy pages if not present in query string
  const currentPath = window.location.pathname;
  if (currentPath.startsWith('/medicine/') || currentPath === '/pharmacies' || currentPath === '/map') {
    const urlParams = new URLSearchParams(window.location.search);
    if (!urlParams.has('lat') && !urlParams.has('lon')) {
      const savedLat = sessionStorage.getItem('user_lat');
      const savedLon = sessionStorage.getItem('user_lon');
      if (savedLat && savedLon) {
        urlParams.set('lat', savedLat);
        urlParams.set('lon', savedLon);
        window.location.replace(`${currentPath}?${urlParams.toString()}`);
      }
    }
  }

  // 3. Google-like Medicine Autocomplete Engine
  const searchInput = document.getElementById('search-input') || document.getElementById('global-search-input') || document.getElementById('home-search-input');
  const suggestionsBox = document.getElementById('ac-dropdown') || document.getElementById('search-suggestions') || document.getElementById('home-ac-dropdown');
  const spinner = document.getElementById('search-spinner');
  const searchForm = document.getElementById('search-form') || document.getElementById('main-search-form') || document.getElementById('home-search-form');

  if (searchInput && suggestionsBox) {
    let debounceTimer = null;
    let selectedIndex = -1;
    let currentSuggestions = [];

    // Helper: Escape HTML characters to prevent XSS / HTML injection
    function escapeHtml(str) {
      if (!str) return '';
      return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
    }

    // Helper: Escape Regex characters
    function escapeRegExp(string) {
      return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    // Helper: Highlight matching search term in text
    function highlightMatch(text, query) {
      if (!text || !query) return text || '';
      const regex = new RegExp(`(${escapeRegExp(query)})`, 'gi');
      return text.replace(regex, '<mark class="highlight-match">$1</mark>');
    }

    // Render suggestions in dropdown
    function renderSuggestions(query, items) {
      currentSuggestions = items || [];
      selectedIndex = -1;

      if (!currentSuggestions || currentSuggestions.length === 0) {
        suggestionsBox.innerHTML = `
          <div class="ac-empty">
            <i class="fa-solid fa-circle-question" style="margin-right: 0.4rem; color: #64748b;"></i>
            No medicines found matching "<strong>${escapeHtml(query)}</strong>"
          </div>
        `;
        suggestionsBox.classList.add('open');
        suggestionsBox.style.display = 'block';
        searchInput.setAttribute('aria-expanded', 'true');
        return;
      }

      const html = currentSuggestions.map((med, index) => {
        const safeName = escapeHtml(med.name);
        const highlightedName = highlightMatch(safeName, escapeHtml(query));
        const subtitle = [med.generic_name, med.dosage_form, med.strength]
          .filter(Boolean)
          .map(escapeHtml)
          .join(' · ');
        const rxBadge = med.requires_prescription 
          ? '<span class="ac-badge-rx">Rx</span>' 
          : '<span class="ac-badge-otc">OTC</span>';
        const safeUrl = encodeURI(med.url || `/medicine/${med.id}`);

        return `
          <div class="ac-item" role="option" id="suggestion-item-${index}" data-index="${index}" data-url="${safeUrl}" tabindex="-1">
            <div class="ac-item-icon">
              <i class="fa-solid fa-pills"></i>
            </div>
            <div class="ac-item-body">
              <div class="ac-item-name">${highlightedName}</div>
              <div class="ac-item-sub">${subtitle}</div>
            </div>
            ${rxBadge}
          </div>
        `;
      }).join('');

      suggestionsBox.innerHTML = html;
      suggestionsBox.classList.add('open');
      suggestionsBox.style.display = 'block';
      searchInput.setAttribute('aria-expanded', 'true');

      // Add click listeners to items
      const domItems = suggestionsBox.querySelectorAll('.ac-item');
      domItems.forEach(el => {
        el.addEventListener('mousedown', (e) => {
          e.preventDefault();
          const url = el.getAttribute('data-url');
          if (url) window.location.href = url;
        });

        el.addEventListener('mouseenter', () => {
          const idx = parseInt(el.getAttribute('data-index'), 10);
          setSelectedIndex(idx, false);
        });
      });
    }

    function setSelectedIndex(newIndex, scroll = true) {
      const items = suggestionsBox.querySelectorAll('.ac-item');
      if (items.length === 0) return;

      if (selectedIndex >= 0 && items[selectedIndex]) {
        items[selectedIndex].classList.remove('focused', 'active');
        items[selectedIndex].removeAttribute('aria-selected');
      }

      selectedIndex = newIndex;
      if (selectedIndex >= items.length) selectedIndex = 0;
      if (selectedIndex < 0) selectedIndex = items.length - 1;

      if (items[selectedIndex]) {
        items[selectedIndex].classList.add('focused', 'active');
        items[selectedIndex].setAttribute('aria-selected', 'true');
        searchInput.setAttribute('aria-activedescendant', `suggestion-item-${selectedIndex}`);
        if (scroll) {
          items[selectedIndex].scrollIntoView({ block: 'nearest', behavior: 'smooth' });
        }
      }
    }

    function closeSuggestions() {
      suggestionsBox.classList.remove('open');
      suggestionsBox.style.display = 'none';
      suggestionsBox.innerHTML = '';
      searchInput.setAttribute('aria-expanded', 'false');
      selectedIndex = -1;
      currentSuggestions = [];
      if (spinner) spinner.style.display = 'none';
    }

    // Input event with debouncing
    searchInput.addEventListener('input', (e) => {
      const q = e.target.value.trim();
      clearTimeout(debounceTimer);

      if (q.length < 2) {
        closeSuggestions();
        return;
      }

      suggestionsBox.innerHTML = '<div class="ac-loading"><i class="fa-solid fa-spinner fa-spin"></i> Searching...</div>';
      suggestionsBox.classList.add('open');
      suggestionsBox.style.display = 'block';
      if (spinner) spinner.style.display = 'inline-block';

      debounceTimer = setTimeout(async () => {
        try {
          const res = await fetch(`/api/medicines/suggestions?q=${encodeURIComponent(q)}`);
          if (!res.ok) throw new Error("Network response error");
          const data = await res.json();
          if (spinner) spinner.style.display = 'none';

          if (searchInput.value.trim() === q && data.status === 'success') {
            renderSuggestions(q, data.suggestions);
          }
        } catch (err) {
          if (spinner) spinner.style.display = 'none';
          suggestionsBox.innerHTML = '<div class="ac-empty text-danger"><i class="fa-solid fa-triangle-exclamation"></i> Unable to load suggestions. Press enter to search.</div>';
          suggestionsBox.classList.add('open');
          suggestionsBox.style.display = 'block';
        }
      }, 200); // 200ms debouncing
    });

    // Keyboard navigation handlers (ArrowUp, ArrowDown, Enter, Escape)
    searchInput.addEventListener('keydown', (e) => {
      const items = suggestionsBox.querySelectorAll('.ac-item');
      const isVisible = suggestionsBox.classList.contains('open') || suggestionsBox.style.display === 'block';

      if (e.key === 'ArrowDown') {
        if (!isVisible && searchInput.value.trim().length >= 2) {
          searchInput.dispatchEvent(new Event('input'));
          return;
        }
        if (isVisible && items.length > 0) {
          e.preventDefault();
          setSelectedIndex(selectedIndex + 1);
        }
      } else if (e.key === 'ArrowUp') {
        if (isVisible && items.length > 0) {
          e.preventDefault();
          setSelectedIndex(selectedIndex - 1);
        }
      } else if (e.key === 'Enter') {
        if (isVisible && selectedIndex >= 0 && currentSuggestions[selectedIndex]) {
          e.preventDefault();
          const targetUrl = currentSuggestions[selectedIndex].url;
          if (targetUrl) {
            window.location.href = targetUrl;
          }
        }
      } else if (e.key === 'Escape') {
        if (isVisible) {
          e.preventDefault();
          closeSuggestions();
        }
      }
    });

    // Click outside to close
    document.addEventListener('click', (e) => {
      if (!searchInput.contains(e.target) && !suggestionsBox.contains(e.target)) {
        closeSuggestions();
      }
    });
  }
});
