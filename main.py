import json
import os
import requests
import numpy
import rasterio
import wget
from stl import mesh
from haversine import haversine

(topLat,leftLong) = (41.503351, -122.347241)
(botLat,rightLong) = (41.296212, -122.029142)

resolution = "1" #options are "1" or "1/3"
heightScalar = 1 #multiplier for height
outputFileName = "test" #name for output file
unit = 'mm' #options are 'm' (metric, 1cm is 1km) or 'in' (imperial, 1in is 1mi)

boxBR = [botLat,rightLong]
boxTL = [topLat,leftLong]


if abs(boxBR[0] - boxTL[0]) > 1 or abs(boxBR[1]-boxTL[1]) > 1 or (resolution == "1/3" and (abs(boxBR[0] - boxTL[0]) > 0.5 or abs(boxBR[1]-boxTL[1]) > 0.5)):
    print("Area too big, pick a new area")
    exit()


absolute_path = os.path.dirname(__file__)

def generateSTL(heights,widthMult,heightMult):

    print("\nGenerating STL file...")
    lenDataset =  len(heights)
    widthDataset =len(heights[0])

    smallest = heights[0][0]
    #print(heights[0][0])
    for row in heights:
        for height in row:
            if (height < smallest):
                smallest = height

    i = 0
    while i < widthDataset:
        j = 0
        while j < lenDataset:
            heights[j][i] = heights[j][i] - smallest
            j +=1
        i+=1

    verticeDepth = -100

    # Define the vertices of the object
    numHeightElements =  lenDataset*widthDataset
    vertices = [[0 for x in range(3)]for y in range(numHeightElements)] #may not be necessary

    #create top vertices
    i = 0
    while i < lenDataset:
        j = 0
        while j <widthDataset:
            vertices[(i*widthDataset)+j][0] = i*widthMult
            vertices[(i*widthDataset)+j][1] = j*heightMult
            vertices[(i*widthDataset)+j][2] = heights[i][j]*heightScalar
            j+=1
        i +=1
    
    #create left vertices
    i = 0
    while i < lenDataset:
        vertices.append([i*widthMult,0,verticeDepth])
        i+=1
    
    #create right vertices
    i = 0
    while i < lenDataset:
        vertices.append([i*widthMult,(widthDataset-1)*heightMult,verticeDepth])
        i+=1

    #create upper side vertices
    i = 0
    while i < widthDataset:
        vertices.append([0,i*heightMult,verticeDepth])
        i+=1

    #create lower side vertices
    i = 0
    while i < widthDataset:
        vertices.append([(lenDataset-1)*widthMult,i*heightMult,verticeDepth])
        i+=1
    print("Vertices complete, creating polygons")
    # Define the triangles composing the object
    faces = []

    #creates the polygons for the top of the surface
    i = 0
    while i < lenDataset:
        j = 0
        while j < widthDataset:
            if ((i+1) < (lenDataset)) & ((j+1) < (widthDataset)):
                faces.append([j+(i*widthDataset),j+1+((i+1)*widthDataset),j+1+(i*widthDataset)])
                faces.append([j+(i*widthDataset),j+((i+1)*widthDataset),j+1+((i+1)*widthDataset)])
            j += 1
        i += 1

    #create the polygons for the left and right side of the surface
    i = 0
    while i < lenDataset:
        if i+1 < lenDataset:
            #left side
            faces.append([i*widthDataset,i+lenDataset*widthDataset+1,(i+1)*widthDataset])
            faces.append([i*widthDataset,i+lenDataset*widthDataset,i+lenDataset*widthDataset+1])

            #right side
            faces.append([i*widthDataset+(widthDataset-1),i+lenDataset*widthDataset+lenDataset+1,i+lenDataset*widthDataset+lenDataset])
            faces.append([i*widthDataset+(widthDataset-1),(i+1)*widthDataset+(widthDataset-1),i+lenDataset*widthDataset+lenDataset+1])
        i+=1

    #create polygons for the upper side and lower side of the surface
    i = 0
    while i < widthDataset:
        if i+1 < widthDataset:
            #upper side
            faces.append([i,i+lenDataset*widthDataset+2*lenDataset+1,i+lenDataset*widthDataset+2*lenDataset])
            faces.append([i,i+1,i+lenDataset*widthDataset+2*lenDataset+1])

            #lower side
            faces.append([i+(widthDataset*(lenDataset-1)),i+lenDataset*widthDataset+2*lenDataset+widthDataset,i+lenDataset*widthDataset+2*lenDataset+widthDataset+1])
            faces.append([i+(widthDataset*(lenDataset-1)),i+lenDataset*widthDataset+2*lenDataset+widthDataset+1,i+(widthDataset*(lenDataset-1))+1])
        i+=1
    
    #add the two polygons for the bottom along with their vertices
    lastStartIndex = len(vertices) #starting point to where the new vertices will be added

    vertices.append([0,0,-10])#top left corner
    vertices.append([0,(widthDataset-1)*heightMult,verticeDepth]) #top right corner
    vertices.append([(lenDataset-1)*widthMult,0,verticeDepth]) #bottom left corner
    vertices.append([(lenDataset-1)*widthMult,(widthDataset-1)*heightMult,verticeDepth]) #bottom right corner

    faces.append([lastStartIndex,lastStartIndex+3,lastStartIndex+2])
    faces.append([lastStartIndex,lastStartIndex+1,lastStartIndex+3])
    vertices = numpy.array(vertices)
    faces = numpy.array(faces)

    print("Polygons complete, scaling and generating mesh")

    # Create the mesh

    if unit == 'm':
        vertices = vertices/100
    elif unit == 'in':
        vertices = vertices*100/6336
    else:
        vertices = vertices/100

    shape = mesh.Mesh(numpy.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    for i, f in enumerate(faces):
        for j in range(3):
            shape.vectors[i][j] = vertices[f[j], :]

    # Write the mesh to file "cube.stl"

    relative_path = "STL_Files/"
    full_path = os.path.join(absolute_path, relative_path)
    fileName = full_path + outputFileName + ".stl"
    #print(fileName)

    shape.save(fileName)
    print("File generated!\n")

def getFiles(botLat,leftLong,topLat,rightLong,resolution):

    boundingBox = str(leftLong)+','+str(botLat)+','+str(rightLong)+','+str(topLat)

    highRes = False

    if(resolution == '1/3'):
        highRes = True
    elif(resolution == '1'):
        highRes = False
    else:
        print("\nInvalid Resolution")
        exit()

    url = "https://tnmaccess.nationalmap.gov/api/v1/products?datasets=National%20Elevation%20Dataset%20(NED)&bbox="+boundingBox+"&prodFormat=GeoTIFF&prodExtents=1%20x%201%20degree"

    payload = {}
    headers = {}

    print("\nAttempting request...")

    response = requests.request("GET", url, headers=headers, data=payload)
    #print(response.text)
    jsonDict = json.loads(response.text)

    print("Request complete")

    #print(jsonDict["items"])

    #a list of all the files that contain the specified bounding box 
    #and their corresponding download urls
    nameUrlDict = {

    }

    count = 0
    resolution1  = ''
    if resolution == '1/3':
        resolution1 = '13'

    for item in jsonDict["items"]:
        if 'USGS ' + resolution + ' Arc ' in item['title'] or 'USGS ' + resolution + ' arc-' in item['title'] or 'USGS ' + resolution1 + ' arc-' in item['title'] or 'USGS ' + resolution1 + ' Arc' in item['title']:
            try:
                if highRes and item['title'][5:8] == '1/3':
                    nameUrlDict['13_' + item['title'][20:27]] = item['urls']["TIFF"] #use 20:27 for 1/3 arc seconds
                elif highRes and item['title'][5:7] == '13':
                    nameUrlDict['13_' + item['title'][19:26]] = item['urls']["TIFF"] #use 20:27 for 1/3 arc seconds
                else:
                    nameUrlDict['1_' + item['title'][18:25]] = item['urls']["TIFF"] #use 18:25 for 1 arc second
                count+=1
            except: KeyError

    #print(nameUrlDict)
    print("\n" + str(count)+" High resolution file(s) found")

    relative_path = "geotiff/"
    full_path = os.path.join(absolute_path, relative_path)

    dir_list = os.listdir(full_path) #list of files in the geotiff folder

    print(str(len(nameUrlDict)) + " file(s) required\n")
    for key in nameUrlDict:
        keyInList = False
        for file in dir_list:
            if key in file:
                print("File " + key + " already downloaded")
                keyInList = True
        if not(keyInList):
            print("Downloading " + key + " file:")
            wget.download(nameUrlDict[key] , full_path)
            print("")
    print("All files acquired")

    # prints all files
    #print(dir_list)

    #print(urlsList[len(urlsList)-1])

    #print(namesList)
    #print(urlsList)

    dir_list = os.listdir(full_path)
    fileList = []
    for name in nameUrlDict:
        i = 0 
        while i < len(dir_list):
            if name in dir_list[i]:
                fileList.append(dir_list[i])
            i +=1

    return fileList

fileList = getFiles(botLat,leftLong,topLat,rightLong,resolution)

#print(fileList)

elevationFull = 0
pixelHeight = 0
pixelWidth = 0

(startRow,startCol) = (0,0)
(endRow,endCol) = (0,0)

print("\nGathering elevation data...")

if (len(fileList)) == 1:
    
    filePath = absolute_path + "/geotiff/" + fileList[0]
    dataset = rasterio.open(filePath)

    dataHeight = dataset.height #number of pixels high, only used for finding true height of one pixel
    dataWidth = dataset.width #number of pixels wide, only used for finding true width of one pixel

    (ULClong, ULClat) = dataset.transform * (0,0) #upper left corner coords
    (LRClong, LRClat) = dataset.transform * (dataset.width,dataset.height) #lower right corner coords

    elevationFull = dataset.read(1) #elevation data for every pixel

    #these take long, lat instead of lat, long
    #generates the indices that correspond to the given latitude and longitude
    (startRow,startCol) = dataset.index(boxTL[1],boxTL[0])
    (endRow,endCol) = dataset.index(boxBR[1],boxBR[0]) 


if (len(fileList)) == 2:
    dataPath0 = absolute_path + "/geotiff/" + fileList[1] #top/left file
    dataPath1 = absolute_path + "/geotiff/" + fileList[0] #bottom/right file

    dataset0 = rasterio.open(dataPath0)
    dataset1 = rasterio.open(dataPath1)

    elevationData0 = dataset0.read(1)
    elevationData1 = dataset1.read(1)

    (ULClong, ULClat) = dataset0.transform * (0,0) #upper left corner coords
    (LRClong, LRClat) = dataset1.transform * (dataset1.width,dataset1.height) #lower right corner coords

    (startRow,startCol) = dataset0.index(boxTL[1],boxTL[0])
    (endRow,endCol) = dataset1.index(boxBR[1],boxBR[0])

    dataWidth0 = dataset0.width
    dataHeight0 = dataset0.height

    dataWidth1 = dataset1.width
    dataHeight1 = dataset1.height
    
    vertical = False #whether or not the file is to be concatenated vertically
    horizontal = False
    if(resolution == '1'):
        if int(fileList[0][8:10]) != int(fileList[1][8:10]):
            vertical = True
        if int(fileList[0][11:14]) != int(fileList[1][11:14]):
            horizontal = True

    elif(resolution == '1/3'):
        if int(fileList[0][9:11]) != int(fileList[1][9:11]):
            vertical = True
        if int(fileList[0][12:15]) != int(fileList[1][12:15]):
            horizontal = True

    else:
        print("Invalid resolution given")
        exit()

    if vertical:
        print("Combining vertically")
        
        #this just seems to be the correct offset for vertically and horizontally appending elevation files
        i = 12
        while i > 0:
            elevationData0 = numpy.delete(elevationData0,i+dataHeight0-13,axis=0)
            i-=1

        dataHeight0 = len(elevationData0) #height of the first file, used for index offset

        elevationFull = numpy.append(elevationData0,elevationData1,axis=0)

        dataWidth = len(elevationFull[0])
        dataHeight = len(elevationFull)

        endRow = endRow + dataHeight0 #offset ending index

        #print(startRow,startCol,endRow,endCol)

    elif horizontal:
        print("Combining laterally")

        #this just seems to be the correct offset for vertically and horizontally appending elevation files
        i = 12
        while i > 0:
            elevationData0 = numpy.delete(elevationData0,i+dataWidth0-13,axis=1)
            i-=1
        
        dataWidth0 = len(elevationData0[0]) #width of the first file, used for the index offset 

        elevationFull = numpy.append(elevationData0,elevationData1,axis=1)
        
        dataWidth = len(elevationFull[0])
        dataHeight = len(elevationFull)

        endCol = endCol + dataWidth0 #offset ending index
    else:
        print("Something has gone amiss")


if (len(fileList)) == 4:
    print("Combining all files")

    dataPath0 = absolute_path + "/geotiff/" + fileList[3] #top left
    dataPath1 = absolute_path + "/geotiff/" + fileList[2] #top right
    dataPath2 = absolute_path + "/geotiff/" + fileList[1] #bottom left 
    dataPath3 = absolute_path + "/geotiff/" + fileList[0] #bottom right 

    dataset0 = rasterio.open(dataPath0)
    dataset1 = rasterio.open(dataPath1)
    dataset2 = rasterio.open(dataPath2)
    dataset3 = rasterio.open(dataPath3)

    elevationData0 = dataset0.read(1) #top left
    elevationData1 = dataset1.read(1) #top right
    elevationData2 = dataset2.read(1) #bottom left
    elevationData3 = dataset3.read(1) #bottom right

    dataWidth0 = dataset0.width
    dataWidth2 = dataset2.width

    (ULClong, ULClat) = dataset0.transform * (0,0) #upper left corner coords
    (LRClong, LRClat) = dataset3.transform * (dataset3.width,dataset3.height) #lower right corner coords

    (startRow,startCol) = dataset0.index(boxTL[1],boxTL[0])
    (endRow,endCol) = dataset3.index(boxBR[1],boxBR[0])

    #combine top left and top right
    i = 12
    while i > 0:
        elevationData0 = numpy.delete(elevationData0,i+dataWidth0-13,axis=1)
        i-=1
    
    dataWidth0 = len(elevationData0[0]) #width of the first file, used for the index offset 
    elevationTop = numpy.append(elevationData0,elevationData1,axis=1)

    #combine bottom left and right
    i = 12
    while i > 0:
        elevationData2 = numpy.delete(elevationData2,i+dataWidth2-13,axis=1)
        i-=1

    dataWidth2 = len(elevationData2[0]) #width of the third file, NOt used for index offset (should be same as dataWidth0)
    elevationBottom = numpy.append(elevationData2,elevationData3,axis=1)

    dataHeight0 = len(elevationTop)

    i = 12
    while i > 0:
        elevationTop = numpy.delete(elevationTop,i+dataHeight0-13,axis=0)
        i-=1

    dataHeight0 = len(elevationData0) #height of the first file, used for index offset
    elevationFull = numpy.append(elevationTop,elevationBottom,axis=0)

    dataHeight = len(elevationFull)
    dataWidth = len(elevationFull[0])

    endRow = endRow + dataHeight0
    endCol = endCol + dataWidth0
    

point1 = (ULClat,ULClong) #upper left corner
point2 = (ULClat,LRClong) #upper right corner
point3 = (LRClat,ULClong) #lower left corner

metersWidth = haversine(point1,point2)*1000 #calculates distance between top corners
metersHeight = haversine(point1,point3)*1000 #calculates distance between left corners

pixelWidth = metersWidth/dataWidth
pixelHeight = metersHeight/dataHeight

#print(pixelHeight,pixelWidth)
#print(pixelHeight/pixelWidth)

#print(elevationData)

#print(startRow,startCol,endRow,endCol)

#generate a smaller dataset to work with instead of the entire map

i = startRow
smallData = numpy.zeros((abs(startRow-endRow),abs(startCol-endCol)))
while i < endRow:
    j = startCol
    while j < endCol:
        smallData[i-startRow][j-startCol] = int(elevationFull[i][j])
        j+=1
    i+=1

#print(startRow,startCol,endRow,endCol)
generateSTL(smallData,pixelHeight,pixelWidth)
