from flask import Flask, Response, request, jsonify, stream_with_context
import subprocess
import folium
from folium.plugins import Draw
from generator import coords2threeD

app = Flask(__name__)

def run_my_program(bbox):
    # Replace with your real processing function
    #print("Running backend program...")
    response = coords2threeD(TL=bbox['max_lat'],LL=bbox['min_lon'],BL=bbox['min_lat'],RL=bbox['max_lon'])
    return {"file_generated_at": bbox, "status": "ok"}

@app.route("/")
def index():
    # Create map
    m = folium.Map(location=[39, -98], zoom_start=4, width="100%", height="100%")
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

    # CSS to fix map size + add a border
    map_id = m.get_name()
    css = f"""
    <style>
      html, body {{ height: auto; margin: 0; padding: 0; }}
      #{map_id} {{
        width: 600px !important;
        height: 400px !important;
        margin: 20px;
        border: 2px solid #000;
      }}
    </style>
    """
    m.get_root().header.add_child(folium.Element(css))

    # Add external JS reference
    script_tag = '<script src="/static/map.js"></script>'
    m.get_root().html.add_child(folium.Element(script_tag))

    # Add button outside the map
    button_html = """
    <div style="text-align:center; margin:10px;">
      <button id="sendButton">Send Rectangle</button>
    </div>
    """
    m.get_root().html.add_child(folium.Element(button_html))

    return m.get_root().render()

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

    bbox = {
        "min_lon": min(lons), "max_lon": max(lons),
        "min_lat": min(lats), "max_lat": max(lats)
    }

    result = run_my_program(bbox)
    return jsonify(result=result)

if __name__ == "__main__":
    app.run(debug=True)
