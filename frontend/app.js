// Initialize map
const map = L.map('map', { zoomControl: false }).setView([18.5204, 73.8567], 17);
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
    attribution: '© ESRI'
  })
};

baseLayers.osm.addTo(map);

// Add 3D buildings button 
let osmb = null;
let osmbEnabled = true;

function toggle3DBuildings() {
  if (osmbEnabled && osmb) {
    osmb.unbind(); // stops drawing and releases resources
    osmb = null;
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

  osmb.date(new Date(Y, M, D, h, 0));
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
document.getElementById('search-input').addEventListener('keypress', function (e) {
  if (e.key === 'Enter') {
    const query = this.value + ', Pune, India';
    fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}`)
      .then(res => res.json())
      .then(data => {
        if (data.length > 0) {
          const lat = parseFloat(data[0].lat);
          const lon = parseFloat(data[0].lon);
          map.setView([lat, lon], 18);
          if (window.searchMarker) map.removeLayer(window.searchMarker);
          window.searchMarker = L.marker([lat, lon])
            .addTo(map)
            .bindPopup(data[0].display_name)
            .openPopup();
        } else {
          alert('Location not found.');
        }
      });
  }
});
