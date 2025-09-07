window.addEventListener('load', function() {
  // Find the Leaflet map instance
  var mapVar = null;
  for (var k in window) {
    if (window[k] instanceof L.Map) { mapVar = window[k]; break; }
  }
  if (!mapVar) { console.error("Leaflet map not found"); return; }

  // Fix tile layout after CSS resize
  setTimeout(function(){ try { mapVar.invalidateSize(); } catch(e) {} }, 200);

  var drawnItems = new L.FeatureGroup();
  mapVar.addLayer(drawnItems);

  var lastLayer = null;

  // Save the last drawn rectangle
  mapVar.on(L.Draw.Event.CREATED, function(e) {
    var layer = e.layer;
    layer.off('click');
    drawnItems.addLayer(layer);
    lastLayer = layer;  
  });

  // When a shape is deleted, update drawnItems + lastLayer
  mapVar.on(L.Draw.Event.DELETED, function(e) {
  drawnItems.clearLayers();
  lastLayer = null;
  });

  // Button click handler
  document.getElementById("sendButton").addEventListener("click", function() {
    if (drawnItems.getLayers().length === 0) {
      alert("Please draw a rectangle first!");
      return;
    }
    var geojson = lastLayer.toGeoJSON();

    fetch('/process', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(geojson)
    })
    .then(r => r.json())
    .then(data => {
      console.log("Server response:", data);
    })
    .catch(err => console.error(err));
  });
});
