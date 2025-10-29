// routing.js
// Handles Valhalla route drawing, clearing, and map interaction
// Updated to support transport mode selection from UI

(function () {
  const routingState = {
    routeLayer: null,
    markers: []
  };

  // -----------------------------
  // Utility Functions
  // -----------------------------
  function addMarker(lat, lon, label) {
    const marker = L.marker([lat, lon]).addTo(map).bindPopup(label);
    routingState.markers.push(marker);
    return marker;
  }

  function clearRouting() {
    if (routingState.routeLayer) {
      map.removeLayer(routingState.routeLayer);
      routingState.routeLayer = null;
    }
    routingState.markers.forEach(m => map.removeLayer(m));
    routingState.markers = [];

    const list = document.getElementById('maneuvers-list');
    if (list) list.innerHTML = '';
    const panel = document.getElementById('maneuvers-panel');
    if (panel) panel.style.display = 'none';
  }

  // -----------------------------
  // Draw GeoJSON Route + Maneuvers
  // -----------------------------
  function drawGeoJSON(geojson) {
    clearRouting(); // Always clear previous route before drawing

    routingState.routeLayer = L.geoJSON(geojson, {
      style: f =>
        f.geometry.type === 'LineString'
          ? { color: '#2b7cff', weight: 5, opacity: 0.95 }
          : {},
      pointToLayer: (f, latlng) =>
        L.circleMarker(latlng, {
          radius: 5,
          fillColor: '#ff6b6b',
          color: '#fff',
          weight: 1,
          fillOpacity: 1
        }),
      onEachFeature: (f, layer) => {
        if (f.properties?.instruction) layer.bindPopup(f.properties.instruction);
      }
    }).addTo(map);

    try {
      map.fitBounds(routingState.routeLayer.getBounds(), { padding: [60, 60] });
    } catch (e) {
      console.warn('fitBounds failed', e);
    }

    const list = document.getElementById('maneuvers-list');
    if (!list) return;

    list.innerHTML = '';
    const points = geojson.features.filter(
      f => f.geometry.type === 'Point' && f.properties?.instruction
    );

    points.forEach(p => {
      const li = document.createElement('li');
      li.innerHTML = `<strong>${p.properties.instruction}</strong><br><small>${(p.properties.length || 0).toFixed(
        2
      )} km · ${(p.properties.time || 0).toFixed(0)} sec</small>`;
      li.addEventListener('click', () => {
        const [lon, lat] = p.geometry.coordinates;
        map.flyTo([lat, lon], Math.max(map.getZoom(), 17), { duration: 0.8 });
      });
      list.appendChild(li);
    });

    if (points.length)
      document.getElementById('maneuvers-panel').style.display = 'block';
  }

  // -----------------------------
  // Fetch Route from Backend (with transport mode support)
  // -----------------------------
  async function requestRouteFromBackend(start, end, costing = 'auto') {
    const url = 'http://localhost:8000/api/valhalla/route/geojson';
    const body = { locations: [start, end], costing };

    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });

    if (!res.ok) throw new Error('Routing failed: ' + (await res.text()));
    return res.json();
  }

  async function getAndDrawRoute(start, end, costing = 'auto') {
    try {
      const btn = document.getElementById('journey-get');
      if (btn) btn.disabled = true;

      const data = await requestRouteFromBackend(start, end, costing);
      if (!data.geojson) throw new Error('No GeoJSON returned');

      drawGeoJSON(data.geojson);
      addMarker(start.lat, start.lon, 'Start');
      addMarker(end.lat, end.lon, 'End');
    } catch (err) {
      alert('Routing error: ' + err.message);
      console.error(err);
    } finally {
      const btn = document.getElementById('journey-get');
      if (btn) btn.disabled = false;
    }
  }

  // -----------------------------
  // Map Click Routing (if user clicks)
  // MODIFIED: Removed auto-route when both points are set
  // -----------------------------
  let startPoint = null;
  let endPoint = null;

  window.setJourneyPoint = function (lat, lon, label = 'Point') {
    if (!startPoint) {
      startPoint = { lat, lon };
      addMarker(lat, lon, 'Start: ' + label);
      document.getElementById('journey-start').value = `${lat.toFixed(
        6
      )}, ${lon.toFixed(6)}`;
      console.log('Start set');
    } else if (!endPoint) {
      endPoint = { lat, lon };
      addMarker(lat, lon, 'End: ' + label);
      document.getElementById('journey-end').value = `${lat.toFixed(
        6
      )}, ${lon.toFixed(6)}`;
      console.log('End set - route will be drawn when "Get Route" is clicked');
      
      // REMOVED: Auto-route invocation
      // Route will only be drawn when user clicks "Get Route" button
      // startPoint and endPoint remain set for the button handler to use
    }
  };

  window.clearJourney = function () {
    startPoint = null;
    endPoint = null;
    clearRouting();
  };

  // -----------------------------
  // Initialize Routing UI
  // -----------------------------
  function initRoutingUI() {
    clearRouting(); // just ensures fresh start
  }

  // -----------------------------
  // Event Listener for app.js "drawRoute"
  // -----------------------------
  window.addEventListener('drawRoute', e => {
    const { geojson, start, end } = e.detail;
    if (!geojson) return;
    drawGeoJSON(geojson);
    addMarker(start.lat, start.lon, 'Start');
    addMarker(end.lat, end.lon, 'End');
  });

  // Export routing helpers
  window.routing = {
    initRoutingUI,
    clearRouting,
    drawGeoJSON,
    getAndDrawRoute
  };
})();