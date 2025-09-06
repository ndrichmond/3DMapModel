from flask import Flask, request, jsonify, render_template
import folium
from folium.plugins import Draw

app = Flask(__name__)

@app.route('/')
def index():
    # Generate map with drawing tool
    m = folium.Map(location=[39, -98], zoom_start=4)
    Draw(export=False).add_to(m)


    mapId = m.get_name()
    # Inject custom JavaScript
    custom_js = """
    <script>
    window.addEventListener("load", function() {
        // Find the folium Leaflet map variable dynamically
        var mapId = null;
        for (var key in window) {
            if (window[key] instanceof L.Map) {
                mapId = window[key];
                break;
            }
        }

        if (!mapId) {
            console.error("No Leaflet map found!");
            return;
        }

        var drawnItems = new L.FeatureGroup();
        mapId.addLayer(drawnItems);

        mapId.on(L.Draw.Event.CREATED, function (e) {
            var layer = e.layer;
            drawnItems.addLayer(layer);

            var geojson = layer.toGeoJSON();
            console.log("Draw event fired:", geojson);

            fetch('/process', {
                method: 'POST',
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(geojson)
            })
            .then(response => response.json())
            .then(data => {
                alert("Server response: " + JSON.stringify(data));
            });
        });
    });
    </script>
    """

    m.get_root().html.add_child(folium.Element(custom_js))

    return m.get_root().render()  # serve the map directly

@app.route('/process', methods=['POST'])
def process():
    data = request.json  # incoming GeoJSON from frontend
    # Extract bounds (lat/lon of rectangle corners)
    coords = data['geometry']['coordinates'][0]  
    # Run your existing program with coords
    result = my_program(coords)  

    print(result)
    return True #jsonify(result=result)

def my_program(coords):
    # Dummy example: just return corners
    return {"corners": coords}

if __name__ == "__main__":
    app.run(debug=True)