import folium
from folium.plugins import Draw
import webbrowser
import os

# Create the map centered on the US
m = folium.Map(location=[39, -98], zoom_start=4)

# Add drawing tools (rectangle, polygon, etc.)
Draw(export=True).add_to(m)

# Save map to an HTML file
map_file = "map.html"
m.save(map_file)

# Open in default browser
full_path = os.path.abspath(map_file)
webbrowser.open("file://" + full_path)