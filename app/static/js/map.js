/**
 * Leaflet.js + OpenStreetMap integration for MediFind
 */

function initPharmacyMap(options = {}) {
  const mapElement = document.getElementById('map-container');
  if (!mapElement) return;

  const defaultLat = options.initialLat || 28.6139;
  const defaultLon = options.initialLon || 77.2090;
  const defaultZoom = options.initialZoom || 12;

  // Initialize Map
  const map = L.map('map-container').setView([defaultLat, defaultLon], defaultZoom);

  // OpenStreetMap Tile Layer
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  }).addTo(map);

  // Custom Icon Helpers
  const verifiedIcon = L.divIcon({
    className: 'custom-map-marker verified',
    html: '<div style="background:#059669; color:#fff; width:34px; height:34px; border-radius:50%; display:flex; align-items:center; justify-content:center; box-shadow:0 3px 8px rgba(0,0,0,0.3); border:2px solid #fff;"><i class="fa-solid fa-check"></i></div>',
    iconSize: [34, 34],
    iconAnchor: [17, 34],
    popupAnchor: [0, -34]
  });

  const standardIcon = L.divIcon({
    className: 'custom-map-marker standard',
    html: '<div style="background:#0284c7; color:#fff; width:34px; height:34px; border-radius:50%; display:flex; align-items:center; justify-content:center; box-shadow:0 3px 8px rgba(0,0,0,0.3); border:2px solid #fff;"><i class="fa-solid fa-prescription-bottle-medical"></i></div>',
    iconSize: [34, 34],
    iconAnchor: [17, 34],
    popupAnchor: [0, -34]
  });

  const userIcon = L.divIcon({
    className: 'custom-map-marker user',
    html: '<div style="background:#dc2626; color:#fff; width:28px; height:28px; border-radius:50%; display:flex; align-items:center; justify-content:center; box-shadow:0 3px 8px rgba(0,0,0,0.3); border:2px solid #fff;"><i class="fa-solid fa-user"></i></div>',
    iconSize: [28, 28],
    iconAnchor: [14, 28],
    popupAnchor: [0, -28]
  });

  // Plot User Location Marker if provided
  if (options.userLat && options.userLon) {
    L.marker([options.userLat, options.userLon], { icon: userIcon })
      .addTo(map)
      .bindPopup('<strong>Your Location</strong>')
      .openPopup();
  }

  // Load Pharmacies from API or static array
  if (options.pharmacies && options.pharmacies.length > 0) {
    const markers = [];
    options.pharmacies.forEach(p => {
      if (!p.latitude || !p.longitude) return;

      const icon = p.is_verified ? verifiedIcon : standardIcon;
      const marker = L.marker([p.latitude, p.longitude], { icon: icon }).addTo(map);

      const verifiedBadgeHtml = p.is_verified
        ? '<span class="badge badge-success"><i class="fa-solid fa-shield-check"></i> Verified</span>'
        : '<span class="badge badge-secondary">Pending Verification</span>';

      const distanceHtml = p.distance_km ? `<div><i class="fa-solid fa-route"></i> ${p.distance_km} km away</div>` : '';
      const stockHtml = p.stock_status ? `<div style="margin-top:4px;"><span class="badge ${p.status_badge_class || 'badge-primary'}">${p.stock_status.replace('_', ' ')}</span></div>` : '';
      const updatedHtml = p.last_updated_human ? `<div style="font-size:0.75rem; color:#64748b; margin-top:4px;"><i class="fa-regular fa-clock"></i> Last updated: ${p.last_updated_human}</div>` : '';

      const popupContent = `
        <div class="map-popup-card">
          <div style="margin-bottom:6px;">${verifiedBadgeHtml}</div>
          <div class="map-popup-title">${p.name || p.pharmacy_name}</div>
          <div class="map-popup-addr">${p.address || ''}, ${p.city || ''}</div>
          ${distanceHtml}
          ${stockHtml}
          ${updatedHtml}
          <div style="margin-top:8px;">
            <a href="/pharmacy/${p.id || p.pharmacy_id}" class="btn btn-sm btn-primary" style="display:block; text-align:center;">View Pharmacy</a>
          </div>
        </div>
      `;

      marker.bindPopup(popupContent);
      markers.push(marker);
    });

    if (markers.length > 0) {
      const group = new L.featureGroup(markers);
      map.fitBounds(group.getBounds().pad(0.15));
    }
  }

  return map;
}
