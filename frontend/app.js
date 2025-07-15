// Initialize Leaflet Map with zoom control at top-right
var map = new L.Map('map', {
  zoomControl: false  // disable default top-left zoom buttons
});
map.setView([18.5204, 73.8567], 17);

// Custom Zoom Control at top-right
L.control.zoom({
  position: 'topright'
}).addTo(map);

// Base Map Layer
new L.TileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '© OpenStreetMap contributors',
  maxZoom: 20
}).addTo(map);

// OSMBuildings 3D Layer
var osmb = new OSMBuildings(map)
  .load('https://{s}.data.osmbuildings.org/0.2/59fcc2e8/tile/{z}/{x}/{y}.json');

// Time/Date controls
var now = new Date();

function pad(v) {
  return (v < 10 ? '0' : '') + v;
}

function updateDateTime() {
  var Y = now.getFullYear(),
      M = now.getMonth(),
      D = now.getDate(),
      h = now.getHours();

  document.getElementById('timeLabel').innerText = pad(h) + ':00';
  var Jan1 = new Date(Y, 0, 1);
  var dayOfYear = Math.ceil((now - Jan1) / 86400000);
  document.getElementById('dateLabel').innerText = dayOfYear;

  osmb.date(new Date(Y, M, D, h, 0));
}

// Listeners for controls
document.getElementById('time').addEventListener('input', function() {
  now.setHours(this.value);
  updateDateTime();
});

document.getElementById('date').addEventListener('input', function() {
  var Jan1 = new Date(now.getFullYear(), 0, 1);
  var newDate = new Date(Jan1.getTime() + (this.value - 1) * 86400000);
  now.setMonth(newDate.getMonth());
  now.setDate(newDate.getDate());
  updateDateTime();
});

// Initial display
updateDateTime();
