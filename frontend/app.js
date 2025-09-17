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
    });
    resultList.appendChild(li);
  });
});

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
// Click map to set location
// ---------------------------
let clickedLatLng = null;
map.on('click', function(e) {
  clickedLatLng = e.latlng;
  if (window.clickMarker) map.removeLayer(window.clickMarker);
  window.clickMarker = L.marker(clickedLatLng).addTo(map)
    .bindPopup("Clicked location set for nearby search.").openPopup();
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
