import json
import requests
import wget
import os
import rasterio
import numpy

absolute_path = os.path.dirname(__file__)

botLat = "38.2"
rightLong = "-121.6"

topLat = "38.136"
leftLong = "-122.4"

def getFiles(botLat,leftLong,topLat,rightLong):

    boundingBox = leftLong+','+botLat+','+rightLong+','+topLat

    url = "https://tnmaccess.nationalmap.gov/api/v1/products?datasets=National%20Elevation%20Dataset%20(NED)&bbox="+boundingBox+"&prodFormat=GeoTIFF&prodExtents=1%20x%201%20degree"

    payload = {}
    headers = {}

    print("Attempting request...")

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

    for item in jsonDict["items"]:
        if 'USGS 1 Arc ' in item['title'] or 'USGS 1 arc-' in item['title']:
            try:
                nameUrlDict[item['title'][18:25]] = item['urls']["TIFF"] #use 20:27 for 1/3 arc seconds
                count+=1
            except: KeyError

    #print(nameUrlDict)
    print("")


    print(str(count)+" High resolution files found")

    relative_path = "geotiff/"
    full_path = os.path.join(absolute_path, relative_path)

    dir_list = os.listdir(full_path) #list of files in the geotiff folder

    print(str(len(nameUrlDict)) + " files required")

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
    print("All files acquired\n")

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

fileList = getFiles(botLat,leftLong,topLat,rightLong)

#print(fileList)

elevationFull = 0

if (len(fileList)) == 2:
    dataPath0 = absolute_path + "/geotiff/"+fileList[1] #top file
    dataPath1 = absolute_path + "/geotiff/"+fileList[0] #bottom file

    dataset0 = rasterio.open(dataPath0)
    dataset1 = rasterio.open(dataPath1)

    elevationData0 = dataset0.read(1)
    elevationData1 = dataset1.read(1)
    
    if int(fileList[0][8:10]) < int(fileList[1][8:10]):
        print("Combining vertically")
        elevationFull = numpy.append(elevationData0,elevationData1,axis=0)
    else:
        print("Combining laterally")
        elevationFull = numpy.append(elevationData0,elevationData1,axis=1)
        #TODO: combine bands right to left

print(len(elevationFull[0]),len(elevationFull))

if (len(fileList)) == 4:
    #TODO:combine all four bands
    print("combining all files")