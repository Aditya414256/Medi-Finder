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

  // 2. Geolocation prompt helper for nearby search
  const geoButtons = document.querySelectorAll('[data-action="get-location"]');
  geoButtons.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      if (!navigator.geolocation) {
        alert("Geolocation is not supported by your browser.");
        return;
      }
      const origHtml = btn.innerHTML;
      btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Locating...';
      btn.disabled = true;

      navigator.geolocation.getCurrentPosition(
        (position) => {
          const lat = position.coords.latitude;
          const lon = position.coords.longitude;
          sessionStorage.setItem('user_lat', lat);
          sessionStorage.setItem('user_lon', lon);
          
          const targetUrl = new URL(window.location.href);
          targetUrl.searchParams.set('lat', lat);
          targetUrl.searchParams.set('lon', lon);
          window.location.href = targetUrl.toString();
        },
        (error) => {
          btn.innerHTML = origHtml;
          btn.disabled = false;
          alert("Unable to retrieve your location. Please check your browser permissions.");
        },
        { timeout: 10000 }
      );
    });
  });

  // 3. Google-like Medicine Autocomplete Engine
  const searchInput = document.getElementById('global-search-input');
  const suggestionsBox = document.getElementById('search-suggestions');
  const spinner = document.getElementById('search-spinner');
  const searchForm = document.getElementById('main-search-form');

  if (searchInput && suggestionsBox) {
    let debounceTimer = null;
    let selectedIndex = -1;
    let currentSuggestions = [];

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
      currentSuggestions = items;
      selectedIndex = -1;

      if (!items || items.length === 0) {
        suggestionsBox.innerHTML = `
          <div class="autocomplete-empty">
            <i class="fa-solid fa-circle-question text-muted" style="margin-right: 0.5rem;"></i>
            No medicines found matching "<strong>${escapeHtml(query)}</strong>"
          </div>
        `;
        suggestionsBox.style.display = 'block';
        searchInput.setAttribute('aria-expanded', 'true');
        return;
      }

      const html = items.map((med, index) => {
        const highlightedName = highlightMatch(med.name, query);
        const highlightedGeneric = highlightMatch(med.generic_name, query);
        const highlightedBrand = med.brand_name ? highlightMatch(med.brand_name, query) : '';
        const rxBadge = med.requires_prescription 
          ? '<span class="badge badge-warning" style="font-size:0.68rem; padding:0.15rem 0.45rem;"><i class="fa-solid fa-prescription"></i> Rx</span>' 
          : '<span class="badge badge-success" style="font-size:0.68rem; padding:0.15rem 0.45rem;">OTC</span>';

        return `
          <div class="autocomplete-item" role="option" id="suggestion-item-${index}" data-index="${index}" data-url="${med.url}">
            <div class="autocomplete-icon">
              <i class="fa-solid fa-pills"></i>
            </div>
            <div class="autocomplete-info">
              <div class="autocomplete-name">
                <span>${highlightedName}</span>
                <span class="badge badge-secondary" style="font-size:0.72rem; padding:0.15rem 0.4rem;">${med.strength}</span>
                ${rxBadge}
              </div>
              <div class="autocomplete-sub">
                ${highlightedGeneric} &bull; ${med.dosage_form}
                ${highlightedBrand ? ` &bull; <span class="text-muted">Brands: ${highlightedBrand}</span>` : ''}
              </div>
            </div>
            <div class="autocomplete-action">
              <i class="fa-solid fa-arrow-right"></i>
            </div>
          </div>
        `;
      }).join('');

      suggestionsBox.innerHTML = html;
      suggestionsBox.style.display = 'block';
      searchInput.setAttribute('aria-expanded', 'true');

      // Add click listeners to items
      const domItems = suggestionsBox.querySelectorAll('.autocomplete-item');
      domItems.forEach(el => {
        el.addEventListener('click', () => {
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
      const items = suggestionsBox.querySelectorAll('.autocomplete-item');
      if (items.length === 0) return;

      if (selectedIndex >= 0 && items[selectedIndex]) {
        items[selectedIndex].classList.remove('active');
        items[selectedIndex].removeAttribute('aria-selected');
      }

      selectedIndex = newIndex;
      if (selectedIndex >= items.length) selectedIndex = 0;
      if (selectedIndex < 0) selectedIndex = items.length - 1;

      if (items[selectedIndex]) {
        items[selectedIndex].classList.add('active');
        items[selectedIndex].setAttribute('aria-selected', 'true');
        searchInput.setAttribute('aria-activedescendant', `suggestion-item-${selectedIndex}`);
        if (scroll) {
          items[selectedIndex].scrollIntoView({ block: 'nearest', behavior: 'smooth' });
        }
      }
    }

    function closeSuggestions() {
      suggestionsBox.style.display = 'none';
      suggestionsBox.innerHTML = '';
      searchInput.setAttribute('aria-expanded', 'false');
      selectedIndex = -1;
      currentSuggestions = [];
      if (spinner) spinner.style.display = 'none';
    }

    function escapeHtml(str) {
      if (!str) return '';
      return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
    }

    // Input event with debouncing
    searchInput.addEventListener('input', (e) => {
      const q = e.target.value.trim();
      clearTimeout(debounceTimer);

      if (q.length < 2) {
        closeSuggestions();
        return;
      }

      if (spinner) spinner.style.display = 'inline-block';

      debounceTimer = setTimeout(async () => {
        try {
          const res = await fetch(`/api/medicines/suggestions?q=${encodeURIComponent(q)}`);
          if (!res.ok) throw new Error("Network response error");
          const data = await res.json();
          if (spinner) spinner.style.display = 'none';

          if (data.status === 'success') {
            renderSuggestions(q, data.suggestions);
          }
        } catch (err) {
          if (spinner) spinner.style.display = 'none';
          suggestionsBox.innerHTML = '<div class="autocomplete-empty text-danger"><i class="fa-solid fa-triangle-exclamation"></i> Unable to load suggestions. Press enter to search.</div>';
          suggestionsBox.style.display = 'block';
        }
      }, 200); // 200ms debouncing
    });

    // Keyboard navigation handlers (ArrowUp, ArrowDown, Enter, Escape)
    searchInput.addEventListener('keydown', (e) => {
      const items = suggestionsBox.querySelectorAll('.autocomplete-item');
      const isVisible = suggestionsBox.style.display === 'block';

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
