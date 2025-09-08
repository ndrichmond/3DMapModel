window.addEventListener('load', function() {

  const loadingOverlay = document.getElementById('LoadingTextOverlay');
  const beginningOverlay = document.getElementById('BeginningTextOverlay');

  function updateLoadingText(newText) {
    loadingOverlay.textContent = newText;
  }

  // Find the Leaflet map instance
  var mapVar = null;
  for (var k in window) {
    if (window[k] instanceof L.Map) { mapVar = window[k]; break; }
  }
  if (!mapVar) { console.error("Leaflet map not found"); return; }

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
    beginningOverlay.style.opacity = "0";
    loadingOverlay.style.opacity = "1"

    // Logs incoming messages about the status of the request
    const eventSource = new EventSource('/stream');
    eventSource.onmessage = function(e) {
      console.log(e.data);
      updateLoadingText(e.data)
      if (e.data === "Complete!") {
        //console.log("Closing SSE");
        modelViewer = document.getElementById('previewModel');
        loadingOverlay.style.opacity = "0";
        modelViewer.src = `/static/glb_files/default.glb?cachebust=${Date.now()}`;
        eventSource.close();
      }
    };

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
