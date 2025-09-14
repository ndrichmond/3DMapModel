from flask import Flask, Response, request, jsonify, render_template
from folium.plugins import Draw
from pathlib import Path
from generator import coords2threeD
import random
import json
import folium
import os


app = Flask(__name__)
bbox = {}

def rmFilesInFolder(folder_path,numFiles,numFilesToDelete=0):
    if getFileCount(folder_path) > numFiles:
        files = []
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path) and filename != "README.md":  # Ensure it's a file, not a subdirectory
                timestamp = os.path.getmtime(file_path)
                files.append((timestamp, file_path))
        files.sort()

        if numFilesToDelete == 0:
            numFilesToDelete = len(files)

        filesToDelete = files[:numFilesToDelete]

        for timestamp, filepath in filesToDelete:
            os.remove(filepath)

def getFileCount(folder_path):
    path = Path(folder_path)
    file_count = sum(1 for item in path.rglob('*') if item.is_file())
    return file_count

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
        "min_lon": min(lons), 
        "max_lon": max(lons),
        "min_lat": min(lats), 
        "max_lat": max(lats),
        "resolution": data["properties"]["resolution"],
        "filename": data["properties"]["name"]
    }

    glbFilePath = os.path.join('static/','glb_files/','gen/')
    stlFilePath = os.path.join('STL_Files/','gen/')
    geotiffFilePath = 'geotiff/'

    rmFilesInFolder(glbFilePath,10,5) #remove all the files if there are more than 10 in the folder
    rmFilesInFolder(stlFilePath,10,5)
    rmFilesInFolder(geotiffFilePath,10,5)

    return {"file_requrested_at": bbox, "status": "ok"}

@app.route("/stream")
def stream():
    def generate():
        try:
            for update in coords2threeD(TL=bbox['max_lat'],LL=bbox['min_lon'],BL=bbox['min_lat'],RL=bbox['max_lon'],resolution=bbox['resolution'],outputFileName=bbox["filename"],taskId=random.randint(1000,9999)):
                yield f"data: {json.dumps(update)}\n\n"
                if update["status"] == "failure":
                    if update["data"] == "fileError":
                        rmFilesInFolder('geotiff/',0)
                    break
        except KeyError:
            yield f"data: {json.dumps({"data": "keyError", "status": "failure"})}"
    return Response(generate(), mimetype='text/event-stream')

if __name__ == "__main__":
    app.run(debug=True)
 