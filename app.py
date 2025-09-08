from flask import Flask, Response, request, jsonify, render_template
import subprocess
import folium
from folium.plugins import Draw
from generator import coords2threeD
import time

app = Flask(__name__)
bbox = {}
def run_my_program(bbox):
    # Replace with your real processing function
    #print("Running backend program...")
    coords2threeD(TL=bbox['max_lat'],LL=bbox['min_lon'],BL=bbox['min_lat'],RL=bbox['max_lon'])
    return {"file_generated_at": bbox, "status": "ok"}

@app.route("/")
def index():
    m = folium.Map(location=[39, -98], zoom_start=4,tiles=None)
    Draw(
        export=False,
        draw_options={
            "polyline": False,
            "polygon": False,
            "circle": False,
            "circlemarker": False,
            "marker": False,
            "rectangle": True
        },
        edit_options={"edit": True, "remove": True}
    ).add_to(m)

    # Street view (OpenStreetMap)
    folium.TileLayer(
        tiles='OpenStreetMap',
        name='Street Map',
        show=True,
        control=True
    ).add_to(m)

    # Satellite view (Esri)
    folium.TileLayer(
        tiles='Esri.WorldImagery',
        name='Satellite',
        show=False,
        control=True
    ).add_to(m)

    folium.LayerControl().add_to(m)

    map_html = m.get_root().render()
    return render_template("index.html", map_html=map_html)

@app.route("/process", methods=["POST"])
def process():
    data = request.json or {}
    coords = data.get('geometry', {}).get('coordinates', [[]])

    ring = coords[0] if coords and isinstance(coords[0], list) else []
    if not ring:
        return jsonify(error="No coordinates received"), 400

    # GeoJSON order = [lon, lat]
    lons = [pt[0] for pt in ring]
    lats = [pt[1] for pt in ring]
    global bbox
    bbox = {
        "min_lon": min(lons), "max_lon": max(lons),
        "min_lat": min(lats), "max_lat": max(lats)
    }

    #result = run_my_program(bbox)
    return {"file_generated_at": bbox, "status": "ok"}

@app.route("/stream")
def stream():
    # Example SSE generator
    def generate():
        for update in coords2threeD(TL=bbox['max_lat'],LL=bbox['min_lon'],BL=bbox['min_lat'],RL=bbox['max_lon']):
            yield f"data: {update}\n\n"
    return Response(generate(), mimetype='text/event-stream')

if __name__ == "__main__":
    app.run(debug=True)
 