window.addEventListener('load', function() {

  const loadingOverlay = document.getElementById('LoadingTextOverlay');
  const beginningOverlay = document.getElementById('BeginningTextOverlay');

  function updateLoadingText(newText) {
    loadingOverlay.textContent = newText;
  }

  //random generator for file names
  function generateRandomAlphanumeric(length) {
  let result = '';
  while (result.length < length) {
    result += Math.random().toString(36).slice(2); 
  }
  return result.slice(0, length); // Trim to the desired length
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
  var fulfillingRequest = false; 
  document.getElementById("sendButton").addEventListener("click", function() {
    if (!fulfillingRequest) {
      if (drawnItems.getLayers().length === 0) {
        updateLoadingText("Please select an area first!");
        beginningOverlay.style.opacity = "0";
        return;
      }
      fulfillingRequest = true
      filename = generateRandomAlphanumeric(15)
      beginningOverlay.style.opacity = "0";
      loadingOverlay.style.opacity = "1";
      // Logs incoming messages about the status of the request
      const eventSource = new EventSource('/stream');
      eventSource.onmessage = function(e) {
      
        console.log(e.data)
        jsObject = JSON.parse(e.data)

        if (jsObject.status === "ok") {
          //console.log(jsObject.data);
          updateLoadingText(jsObject.data);
          if (jsObject.data === "Complete!") {
            //console.log("Closing SSE");
            modelViewer = document.getElementById('previewModel');
            loadingOverlay.style.opacity = "0";
            modelViewer.src = `/static/glb_files/gen/${filename}.glb`;
            eventSource.close();
            fulfillingRequest = false;
          }
        }
        else if (jsObject.status === "failure") {
          if (jsObject.data === 'massiveArea') {
            updateLoadingText("Area too large!")
          }
          else if (jsObject.data === 'fileError') {
            updateLoadingText("File error, please try again or refresh the page")
          }
          else if (jsObject.data === 'keyError') {
            updateLoadingText("keyError, try again?")
          }
          else {
            updateLoadingText("Unknown error, please try again or refresh the page")
          }
          console.log(jsObject.data)
          eventSource.close()
          fulfillingRequest = false
        }
      };

      var geojson = lastLayer.toGeoJSON();
      if (document.getElementById("toggle1").checked) {
        geojson.properties.resolution = "1/3"
      }
      else {
        geojson.properties.resolution = "1"
      }
      geojson.properties.name = filename

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
    }
    else {
      updateLoadingText("Please wait for the previous request to complete")
    }

  });
});
