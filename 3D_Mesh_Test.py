import numpy
from stl import mesh

heightData = [
 [3827, 3831, 3834, 3837, 3840, 3843, 3845, 3846, 3847, 3848, 3848,],
 [3834, 3837, 3840, 3843, 3846, 3848, 3850, 3851, 3852, 3852, 3853,],
 [3840, 3843, 3846, 3849, 3851, 3854, 3856, 3857, 3858, 3858, 3858,],
 [3848, 3850, 3852, 3855, 3857, 3860, 3862, 3863, 3863, 3863, 3863,],
 [3855, 3857, 3859, 3861, 3864, 3865, 3867, 3868, 3869, 3869, 3868,],
 [3863, 3865, 3867, 3868, 3870, 3872, 3873, 3874, 3874, 3874, 3874,],
 [3872, 3874, 3875, 3877, 3878, 3879, 3879, 3880, 3880, 3880, 3880,],
 [3881, 3882, 3883, 3884, 3885, 3885, 3885, 3886, 3885, 3885, 3885,],
 #[3887, 3888, 3889, 3891, 3891, 3892, 3892, 3891, 3891, 3891, 3890,],
 #[3893, 3895, 3897, 3898, 3898, 3899, 3898, 3898, 3897, 3896, 3895,],
 #[3898, 3901, 3903, 3904, 3904, 3904, 3904, 3903, 3903, 3902, 3900,]
 ]

'''
heightData = [
    [1,2,3,4],
    [2,5,4,2],
    [3,1,4,4],
    [4,2,1,4]
]
'''
w = 10
h = 10

def generateSTL(heights,widthMult,heightMult):
    lenDataset =  len(heights)
    widthDataset =len(heights[0])

    #TODO: add bottom and sides of the object
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
            vertices[(i*widthDataset)+j][2] = heights[i][j]
            j+=1
        i +=1
    
    #create left vertices
    i = 0
    while i < lenDataset:
        vertices.append([i*widthMult,0,-1])
        i+=1
    
    #create right vertices
    i = 0
    while i < lenDataset:
        vertices.append([i*widthMult,(widthDataset-1)*heightMult,-1])
        i+=1

    #create upper side vertices
    i = 0
    while i < widthDataset:
        vertices.append([0,i*heightMult,-1])
        i+=1

    #create lower side vertices
    i = 0
    while i < widthDataset:
        vertices.append([(lenDataset-1)*widthMult,i*heightMult,-1])
        i+=1

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

    vertices.append([0,0,-1])
    vertices.append([0,(widthDataset-1)*widthMult,-1])
    vertices.append([(lenDataset-1)*heightMult,0,-1])
    vertices.append([(lenDataset-1)*heightMult,(widthDataset-1)*widthMult,-1])

    faces.append([lastStartIndex,lastStartIndex+3,lastStartIndex+2])
    faces.append([lastStartIndex,lastStartIndex+1,lastStartIndex+3])
    vertices = numpy.array(vertices)
    faces = numpy.array(faces)


    print(vertices)
    print(len(vertices))
    print("")
    print(faces)


    # Create the mesh
    shape = mesh.Mesh(numpy.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    for i, f in enumerate(faces):
        for j in range(3):
            shape.vectors[i][j] = vertices[f[j], :]

    # Write the mesh to file "cube.stl"
    shape.save('surface.stl')
    print("File generated!")

generateSTL(heightData,w,h)