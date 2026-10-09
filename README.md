This repo contains all test files that went into creating the main script, as well as the main script itself. 

The script uses publicly available USGS topological data to generate a 3D model of any rectangular area (as long as it is reasonable in size) in the US.
If you wish to download and use the script yourself, you must ensure that all required packages are installed in the "requirements.txt" file.

The current version can run a local website where a graphical interface can be used to more easily generate areas where desired. To do this, simply run the "app.py" python script. Otherwise, use the generator.py script and manually input coordinates. Regardless of the method used, a .stl file will be generated in the STL_Files folder, ready to be used. Currently, it will generate with a random name. 

To get things running, download the code as a .zip file and unizip it wherever you like. Then, create a virtual python environment and install everything in the requirements.txt file.

This can be done in a variety of ways; for example, using VSCode, create a virtual environment (.venv) and upon creation, install dependencies, or, once activated (using ```source .venv/bin/activate```), run ```python3 -m pip install -r requirements.txt```. 

Inside the activated virtual environment, simply run ```python3 app.py``` (or use any method to run app.py). This will create a local server on http://127.0.0.1:5000. Either type that into a web browser or click the provided link in the terminal.
