// Initialize map
const map = L.map('map', {
  center: [18.5204, 73.8567], // Pune
  zoom: 15,
  minZoom: 15,
  maxZoom: 24,
  zoomControl: false
});

L.control.zoom({ position: 'topright' }).addTo(map);

// Base Layers
const baseLayers = {
  osm: L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '© OpenStreetMap contributors' }),
  carto: L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', { attribution: '© CartoDB' }),
  esri: L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
    attribution: 'Sources: Esri, DigitalGlobe, GeoEye, i-cubed, USDA FSA, USGS, AEX, Getmapping, Aerogrid, IGN, IGP, swisstopo, and the GIS User Community'
  })
};
baseLayers.osm.addTo(map);

// 3D Buildings toggle
let osmb = null;
let osmbEnabled = false;
function toggle3DBuildings() {
  if (osmbEnabled) {
    document.querySelectorAll('canvas').forEach(el => { if (el.style.position === 'absolute') el.remove(); });
    osmbEnabled = false;
  } else {
    osmb = new OSMBuildings(map).load('https://{s}.data.osmbuildings.org/0.2/59fcc2e8/tile/{z}/{x}/{y}.json');
    osmbEnabled = true;
  }
}

// Basemap toggle
function changeBasemap(type) {
  Object.values(baseLayers).forEach(layer => map.removeLayer(layer));
  baseLayers[type].addTo(map);
}
function toggleBasemapPanel() {
  const panel = document.getElementById('basemapPanel');
  panel.style.display = (panel.style.display === 'block') ? 'none' : 'block';
}

// Time & shadow controls
let now = new Date();
function pad(v) { return (v < 10 ? '0' : '') + v; }
function updateDateTime() {
  const Y = now.getFullYear(), M = now.getMonth(), D = now.getDate(), h = now.getHours();
  document.getElementById('timeLabel').innerText = pad(h) + ':00';
  const Jan1 = new Date(Y, 0, 1);
  const dayOfYear = Math.ceil((now - Jan1) / 86400000);
  document.getElementById('dateLabel').innerText = dayOfYear;
  if (osmb) osmb.date(new Date(Y, M, D, h, 0));
}
document.getElementById('time').addEventListener('input', e => { now.setHours(e.target.value); updateDateTime(); });
document.getElementById('date').addEventListener('input', e => {
  const Jan1 = new Date(now.getFullYear(), 0, 1);
  const newDate = new Date(Jan1.getTime() + (e.target.value - 1) * 86400000);
  now.setMonth(newDate.getMonth()); now.setDate(newDate.getDate());
  updateDateTime();
});
updateDateTime();

// ---------------------------
// Main Search Bar
// ---------------------------
let selectedIndex = -1;
let lastLatLng = null; // last geocoded point
const searchInput = document.getElementById('search-input');
const resultList = document.createElement('ul');
resultList.id = 'results-list';
document.getElementById('search-container').appendChild(resultList);

searchInput.addEventListener('input', async function () {
  const query = this.value.trim();
  if (query.length < 2) return;

  // Pelias autocomplete
  const res = await fetch(`http://localhost:4000/v1/autocomplete?text=${encodeURIComponent(query)}`);
  const data = await res.json();

  resultList.innerHTML = '';
  if (!data.features || data.features.length === 0) return;

  data.features.forEach(feature => {
    const li = document.createElement('li');
    li.textContent = feature.properties.label;
    li.addEventListener('click', () => {
      const [lon, lat] = feature.geometry.coordinates;
      lastLatLng = { lat, lon };
      map.setView([lat, lon], 18);
      if (window.searchMarker) map.removeLayer(window.searchMarker);
      window.searchMarker = L.marker([lat, lon]).addTo(map)
        .bindPopup(`<b>${feature.properties.label}</b>`).openPopup();
      resultList.innerHTML = '';
      searchInput.value = feature.properties.label;
      showPlaceHistory(feature.properties.label);
        // 👇 If routing mode is active, use this as start or end point
            // 👇 If journey mode is active, use this as start or end point
      if (journeyActive && window.setJourneyPoint) {
        window.setJourneyPoint(lat, lon, feature.properties.label);
        return; // stop normal flow
      }

    });
    resultList.appendChild(li);
  });
});

async function showPlaceHistory(placeName) {
  try {
    const res = await fetch(`http://localhost:8000/api/history?place=${encodeURIComponent(placeName)}`);
    const data = await res.json();

    // Show history panel
    document.getElementById('history-panel').style.display = 'block';
    document.getElementById('hist-title').innerText = data.title || 'No title found';
    document.getElementById('hist-text').innerText = data.description || 'No history available.';
    document.getElementById('hist-link').href = data.url || '#';
    document.getElementById('hist-link').style.display = data.url ? 'inline' : 'none';

    if (data.image) {
      document.getElementById('hist-img').src = data.image;
      document.getElementById('hist-img').style.display = 'block';
    } else {
      document.getElementById('hist-img').style.display = 'none';
    }
  } catch (err) {
    console.error('Error in showPlaceHistory:', err);
    document.getElementById('history-panel').style.display = 'block';
    document.getElementById('hist-title').innerText = 'No history found';
    document.getElementById('hist-text').innerText = '';
    document.getElementById('hist-img').style.display = 'none';
    document.getElementById('hist-link').style.display = 'none';
  }
}

// Decision logic on Enter key
searchInput.addEventListener('keydown', async (e) => {
  if (e.key !== 'Enter') return;

  e.preventDefault();
  const items = document.querySelectorAll('#results-list li');
  let query = '';
  if (selectedIndex >= 0 && selectedIndex < items.length) query = items[selectedIndex].textContent;
  else query = searchInput.value.trim();

  // Check if query matches a location
  const peliasRes = await fetch(`http://localhost:4000/v1/autocomplete?text=${encodeURIComponent(query)}`);
  const peliasData = await peliasRes.json();

  if (peliasData.features && peliasData.features.length > 0) {
    // It's a location → pick the first result
    const [lon, lat] = peliasData.features[0].geometry.coordinates;
    lastLatLng = { lat, lon };
    map.setView([lat, lon], 18);
    if (window.searchMarker) map.removeLayer(window.searchMarker);
    window.searchMarker = L.marker([lat, lon]).addTo(map)
      .bindPopup(`<b>${peliasData.features[0].properties.label}</b>`).openPopup();
    showPlaceHistory(peliasData.features[0].properties.label);
  } else {
    // No location → treat as AI query
    await performAiSearch(query);
  }

  resultList.innerHTML = '';
  selectedIndex = -1;
});

function updateActiveItem(items) {
  items.forEach((item, idx) => {
    if (idx === selectedIndex) { item.classList.add('active'); item.scrollIntoView({ block: 'nearest' }); }
    else { item.classList.remove('active'); }
  });
}

// ---------------------------
// Nearby Button
// ---------------------------
document.getElementById('nearby-btn').addEventListener('click', async () => {
  const keyword = document.getElementById('keyword-input').value.trim();
  if (!keyword) { alert('Please enter a keyword like temple, bus, hospital'); return; }

  const location = lastLatLng || clickedLatLng;
  if (!location) { alert('Please search or click on the map to set a location.'); return; }

  if (window.resultLayer) window.resultLayer.clearLayers();
  else window.resultLayer = L.layerGroup().addTo(map);

  const url = `http://localhost:8000/api/nearby?lat=${location.lat}&lon=${location.lon}&type=${keyword}&distance=1000`;
  const res = await fetch(url);
  const data = await res.json();
  if (!data.features || data.features.length === 0) { alert("No results found."); return; }

  data.features.forEach(f => {
    const geom = JSON.parse(f.geometry);
    const layer = L.geoJSON(geom).bindPopup(`<b>${f.name || 'Unnamed'}</b><br>${f.fclass || ''}<br>Source: ${f.source}`);
    window.resultLayer.addLayer(layer);
  });

  alert(data.message);
});

// ---------------------------
// Unified map click handler (handles Journey & Nearby & default click)
// ---------------------------
let clickedLatLng = null;

window.nearbyModeActive = false; // default off

map.on('click', async function (e) {
  const { lat, lng } = e.latlng;

  // 1) If Journey Mode active and a field is selected => set journey point
  if (journeyActive && selectedField) {
    // set field values and journeyPoints (app.js uses journeyPoints)
    if (selectedField === 'start') {
      journeyPoints.start = { lat, lon: lng };
      document.getElementById('journey-start').value = `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
    } else {
      journeyPoints.end = { lat, lon: lng };
      document.getElementById('journey-end').value = `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
    }
    // Also notify routing.js (it will handle adding markers / drawing if using setJourneyPoint)
    if (window.setJourneyPoint) window.setJourneyPoint(lat, lng, "Map click");
    // after one click, clear selectedField so user explicitly focuses again if needed
    selectedField = null;
    return;
  }

  // 2) If Nearby Mode active => perform nearby search at clicked point
  if (window.nearbyModeActive) {
    const keyword = document.getElementById('keyword-input').value.trim();
    if (!keyword) { alert('Please enter a keyword like temple, bus, hospital'); return; }

    // prepare result layer
    if (window.resultLayer) window.resultLayer.clearLayers();
    else window.resultLayer = L.layerGroup().addTo(map);

    try {
      const url = `http://localhost:8000/api/nearby?lat=${lat}&lon=${lng}&type=${encodeURIComponent(keyword)}&distance=1000`;
      const res = await fetch(url);
      const data = await res.json();
      if (!data.features || data.features.length === 0) { alert("No results found."); }
      else {
        data.features.forEach(f => {
          const geom = JSON.parse(f.geometry);
          const layer = L.geoJSON(geom).bindPopup(`<b>${f.name || 'Unnamed'}</b><br>${f.fclass || ''}<br>Source: ${f.source}`);
          window.resultLayer.addLayer(layer);
        });
        alert(data.message || `Found ${data.features.length} results.`);
      }
    } catch (err) {
      console.error('Nearby search failed', err);
      alert('Nearby search failed: ' + err.message);
    }

    // Auto-disable nearby mode after one search (optional). Remove next two lines to keep it active.
    window.nearbyModeActive = false;
    const nearbyBtn = document.getElementById('nearby-btn');
    if (nearbyBtn) nearbyBtn.style.background = '';
    return;
  }

  // 3) Default (no mode active): set a simple clicked marker for manual use (like your previous click)
  clickedLatLng = e.latlng;
  if (window.clickMarker) map.removeLayer(window.clickMarker);
  window.clickMarker = L.marker(clickedLatLng).addTo(map)
    .bindPopup("Clicked location set. Use Nearby or search to continue.").openPopup();
});



// ---------------------------
// AI Search
// ---------------------------
async function performAiSearch(query) {
  console.log(`Sending AI query: ${query}`);
  try {
    const response = await fetch('http://localhost:8000/ai-search', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ query })
    });

    const result = await response.json();
    if (!response.ok) { console.error('AI search failed:', result); alert('AI search failed: ' + (result.detail || 'Unknown error')); return; }

    if (window.resultLayer) window.resultLayer.clearLayers();
    else window.resultLayer = L.layerGroup().addTo(map);

    result.features.forEach(f => {
      const layer = L.geoJSON(f.geometry).bindPopup(`<b>${f.properties.name || 'Unnamed'}</b><br>${f.properties.fclass || ''}`);
      window.resultLayer.addLayer(layer);
    });

    alert(`AI search returned ${result.features.length} results.`);
  } catch (err) {
    console.error(err); alert(err.message);
  }
}

// ---------------------------
// 🚗 Valhalla Journey Mode (Pelias + Map Click Integration)
// ---------------------------

const startJourneyBtn = document.getElementById('journey-button');
const exitJourneyBtn = document.getElementById('exit-journey-button');
const journeyPanel = document.getElementById('journey-panel');
const journeyStart = document.getElementById('journey-start');
const journeyEnd = document.getElementById('journey-end');
const journeyGet = document.getElementById('journey-get');
const journeyCancel = document.getElementById('journey-cancel');

let journeyActive = false;
let selectedField = null; // "start" | "end"
let journeyPoints = { start: null, end: null };

// ---------------------------
// Start Journey Mode
// ---------------------------
startJourneyBtn.addEventListener('click', () => {
  journeyActive = true;
  journeyPanel.style.display = 'block';
  startJourneyBtn.style.display = 'none';
  exitJourneyBtn.style.display = 'inline-block';
  selectedField = null;
  journeyPoints = { start: null, end: null };

  if (window.routing && window.routing.clearRouting) window.routing.clearRouting();
  alert('🚗 Journey mode activated!\nClick inside Start or End box, then click map or type to search.');
  journeyStart.focus();
});

// ---------------------------
// Exit Journey Mode
// ---------------------------
exitJourneyBtn.addEventListener('click', () => {
  journeyActive = false;
  journeyPanel.style.display = 'none';
  exitJourneyBtn.style.display = 'none';
  startJourneyBtn.style.display = 'inline-block';
  selectedField = null;
  journeyPoints = { start: null, end: null };

  // 🧹 Clear markers and route when exiting journey
  if (window.routing && typeof window.routing.clearRouting === 'function') {
    window.routing.clearRouting();
  }
  if (window.clearJourney) window.clearJourney();

  alert('❌ Journey mode exited and route cleared.');
});


// ---------------------------
// When user focuses on input box
// ---------------------------
journeyStart.addEventListener('focus', () => selectedField = 'start');
journeyEnd.addEventListener('focus', () => selectedField = 'end');

// ---------------------------
// Map click sets whichever field is active
// ---------------------------
map.on('click', e => {
  if (!journeyActive || !selectedField) return;
  const { lat, lng } = e.latlng;

  if (selectedField === 'start') {
    journeyPoints.start = { lat, lon: lng };
    journeyStart.value = `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
  } else if (selectedField === 'end') {
    journeyPoints.end = { lat, lon: lng };
    journeyEnd.value = `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
  }
});

// ---------------------------
// Pelias geocode for typing search (auto sets start/end)
// ---------------------------
async function geocodeJourneyInput(input, field) {
  const query = input.value.trim();
  if (query.length < 3) return;
  try {
    const res = await fetch(`http://localhost:4000/v1/autocomplete?text=${encodeURIComponent(query)}`);
    const data = await res.json();
    if (data.features && data.features[0]) {
      const [lon, lat] = data.features[0].geometry.coordinates;
      journeyPoints[field] = { lat, lon };
      map.setView([lat, lon], 17);
      L.marker([lat, lon])
        .addTo(map)
        .bindPopup(`${field === 'start' ? 'Start' : 'End'}: ${data.features[0].properties.label}`)
        .openPopup();
    }
  } catch (err) {
    console.error('Pelias geocode failed:', err);
  }
}

journeyStart.addEventListener('input', () => geocodeJourneyInput(journeyStart, 'start'));
journeyEnd.addEventListener('input', () => geocodeJourneyInput(journeyEnd, 'end'));

// ---------------------------
// Request route from FastAPI Valhalla proxy
// ---------------------------
journeyGet.addEventListener('click', async () => {
  if (!journeyPoints.start || !journeyPoints.end) {
    alert('⚠️ Please set both start and end locations.');
    return;
  }

  try {
    const res = await fetch('http://localhost:8000/api/valhalla/route/geojson', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        locations: [journeyPoints.start, journeyPoints.end],
        costing: 'auto'
      })
    });

    const data = await res.json();
    if (!data.geojson) throw new Error('No route data received.');

    // Clear any previous route
    if (window.routing && window.routing.clearRouting) window.routing.clearRouting();

    // Dispatch event for routing.js to draw
    const event = new CustomEvent('drawRoute', {
      detail: {
        geojson: data.geojson,
        start: journeyPoints.start,
        end: journeyPoints.end
      }
    });
    window.dispatchEvent(event);
  } catch (err) {
    console.error('Routing error:', err);
    alert('Failed to fetch route: ' + err.message);
  }
});

// ---------------------------
// Cancel Journey (stays in mode, just resets inputs)
// ---------------------------
journeyCancel.addEventListener('click', () => {
  // Clear input fields
  journeyStart.value = '';
  journeyEnd.value = '';

  // Reset selection and journey data
  selectedField = null;
  journeyPoints = { start: null, end: null };

  // Hide journey panel
  journeyPanel.style.display = 'none';

  // 🔹 Clear route + markers (from routing.js)
  if (window.routing && typeof window.routing.clearRouting === 'function') {
    window.routing.clearRouting();
  }

  // 🔹 Also call clearJourney() to reset any internal state
  if (window.clearJourney) window.clearJourney();

  // Reset journey mode flags
  journeyActive = false;
  window.routingModeActive = false;

});


// ---------------------------
// Initialize routing UI (if routing.js present)
// ---------------------------
if (window.routing && typeof window.routing.initRoutingUI === 'function') {
  window.routing.initRoutingUI();
}




