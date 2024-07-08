This repo contains all test files that went into creating the main script, as well as the main script itself. 

The script uses publicly available USGS topological data to generate a 3D model of any rectangular area (as long as it is reasonable in size) in the US.
If you wish to download and use the script yourself, you must ensure that all required packages are installed, namely:
    - json --> required for dealing with API
    - requests --> required for dealing with API
    - numpy --> math
    - haversine --> math
    - rasterio --> data conversion (allowing the geotiff files to be interpreted)
    - wget --> downloading topological files
    - stl (the package name is called numpy-stl) --> 3D model generation

The only required files are main.py and the two folders, everything else was used for various tests.
