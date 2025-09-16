// Initialize map
const map = L.map('map', {
  center: [18.5204, 73.8567], // Pune
  zoom: 15,
  minZoom: 15,
  maxZoom: 24,
  zoomControl: false //higher zoom
});

L.control.zoom({ position: 'topright' }).addTo(map);

// Base Layers
const baseLayers = {
  osm: L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
  }),
  carto: L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    attribution: '© CartoDB'
  }),
  esri: L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
    attribution: 'Sources: Esri, DigitalGlobe, GeoEye, i-cubed, USDA FSA, USGS, AEX, Getmapping, Aerogrid, IGN, IGP, swisstopo, and the GIS User Community'
  })
};

baseLayers.osm.addTo(map);

// Add 3D buildings button 
let osmb = null;
let osmbEnabled = false;

function toggle3DBuildings() {
  if (osmbEnabled) {
    document.querySelectorAll('canvas').forEach(el => {
      if (el.style.position === 'absolute') el.remove();
    });
    osmbEnabled = false;
  } else {
    osmb = new OSMBuildings(map).load(
      'https://{s}.data.osmbuildings.org/0.2/59fcc2e8/tile/{z}/{x}/{y}.json'
    );
    osmbEnabled = true;
  }
}


// Toggle basemap
function changeBasemap(type) {
  Object.values(baseLayers).forEach(layer => map.removeLayer(layer));
  baseLayers[type].addTo(map);
}

// Toggle basemap panel
function toggleBasemapPanel() {
  const panel = document.getElementById('basemapPanel');
  panel.style.display = (panel.style.display === 'block') ? 'none' : 'block';
}

// Time and shadow control
let now = new Date();

function pad(v) {
  return (v < 10 ? '0' : '') + v;
}

function updateDateTime() {
  const Y = now.getFullYear();
  const M = now.getMonth();
  const D = now.getDate();
  const h = now.getHours();

  document.getElementById('timeLabel').innerText = pad(h) + ':00';
  const Jan1 = new Date(Y, 0, 1);
  const dayOfYear = Math.ceil((now - Jan1) / 86400000);
  document.getElementById('dateLabel').innerText = dayOfYear;

  if (osmb) {
    osmb.date(new Date(Y, M, D, h, 0));
  }
}


document.getElementById('time').addEventListener('input', function () {
  now.setHours(this.value);
  updateDateTime();
});

document.getElementById('date').addEventListener('input', function () {
  const Jan1 = new Date(now.getFullYear(), 0, 1);
  const newDate = new Date(Jan1.getTime() + (this.value - 1) * 86400000);
  now.setMonth(newDate.getMonth());
  now.setDate(newDate.getDate());
  updateDateTime();
});

updateDateTime();

// Geocoding search
let selectedIndex = -1;
let lastLatLng = null; // Store last geocoded point globally
const searchInput = document.getElementById('search-input');

const resultList = document.createElement('ul');
resultList.id = 'results-list';
document.getElementById('search-container').appendChild(resultList);

searchInput.addEventListener('input', async function () {
  const query = this.value.trim();
  if (query.length < 2) return;

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
        .bindPopup(`<b>${feature.properties.label}</b>`)
        .openPopup();
      resultList.innerHTML = '';
      searchInput.value = feature.properties.label;

    });
    resultList.appendChild(li);
  });
});


searchInput.addEventListener('keydown', (e) => {
  const items = document.querySelectorAll('#results-list li');
  if (!items.length) return;

  if (e.key === 'ArrowDown') {
    e.preventDefault();
    selectedIndex = (selectedIndex + 1) % items.length;
    updateActiveItem(items);
  } else if (e.key === 'ArrowUp') {
    e.preventDefault();
    selectedIndex = (selectedIndex - 1 + items.length) % items.length;
    updateActiveItem(items);
  } else if (e.key === 'Enter') {
    e.preventDefault();
    if (selectedIndex >= 0 && selectedIndex < items.length) {
      items[selectedIndex].click();
    } else {
      // Default to first item if none selected
      items[0].click();
    }
  } else if (e.key === 'Escape') {
    // Optional: close dropdown with ESC
    resultList.innerHTML = '';
    selectedIndex = -1;
  }
});


function updateActiveItem(items) {
  items.forEach((item, idx) => {
    if (idx === selectedIndex) {
      item.classList.add('active');
      item.scrollIntoView({ block: 'nearest' });
    } else {
      item.classList.remove('active');
    }
  });
}

document.getElementById('nearby-btn').addEventListener('click', async () => {
  const keyword = document.getElementById('keyword-input').value.trim();
  if (!keyword) {
  alert('Please enter a keyword like temple, bus, hospital etc.');
  return;
}

const location = lastLatLng || clickedLatLng;
// const location = clickedLatLng || lastLatLng;

if (!location) {
  alert('Please search or click on the map to set a location.');
  return;
}


  // Clear previous results
  if (window.resultLayer) {
    window.resultLayer.clearLayers();
  } else {
    window.resultLayer = L.layerGroup().addTo(map);
  }

  const url = `http://localhost:8000/api/nearby?lat=${location.lat}&lon=${location.lon}&type=${keyword}&distance=1000`;
  const res = await fetch(url);
  const data = await res.json();

  if (!data.features || data.features.length === 0) {
    alert("No results found.");
    return;
  }

  data.features.forEach(f => {
    const geom = JSON.parse(f.geometry);
    const layer = L.geoJSON(geom).bindPopup(`<b>${f.name || 'Unnamed'}</b><br>${f.fclass || ''}<br>Source: ${f.source}`);
    window.resultLayer.addLayer(layer);
  });

  alert(data.message); // Show message like: Found 3 temples within 1000m
});
document.getElementById('history-btn').addEventListener('click', async () => {
  const place = searchInput.value.trim();
  if (!place) {
    alert("Please search for a place first.");
    return;
  }

  const res = await fetch(`http://localhost:8000/api/history?place=${encodeURIComponent(place)}`);
  const data = await res.json();

  if (data.error) {
    alert("History not found.");
    return;
  }

  // Show in a sidebar or popup
  document.getElementById("history-panel").style.display = "block";
  document.getElementById("hist-title").innerText = data.title;
  document.getElementById("hist-text").innerText = data.description;
  document.getElementById("hist-link").href = data.url;
  if (data.image) {
    document.getElementById("hist-img").src = data.image;
  } else {
    document.getElementById("hist-img").style.display = "none";
  }
});
let clickedLatLng = null;
map.on('click', function(e) {
  clickedLatLng = e.latlng;

  // Optional: show marker for user feedback
  if (window.clickMarker) {
    map.removeLayer(window.clickMarker);
  }
  window.clickMarker = L.marker(clickedLatLng).addTo(map)
    .bindPopup("Clicked location set for nearby search.")
    .openPopup();
});
