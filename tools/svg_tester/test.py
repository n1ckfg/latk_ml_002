import sys
from svgpathtools import *
from PIL import Image

sys.path.insert(0, '../../latk.py')
from latk import *

def getCoordFromPathPoint(pt):
    point = str(pt)
    point = point.replace("(","")
    point = point.replace("j)","")
    point = point.split("+")
    x = float(point[0])
    y = float(point[1])
    return (x, y)

def getDistance2D(v1, v2):
    v1 = (v1[0], v1[1], 0)
    v2 = (v2[0], v2[1], 0)
    return sqrt((v1[0] - v2[0])**2 + (v1[1] - v2[1])**2 + (v1[2] - v2[2])**2)

def getDistance(v1, v2):
    return sqrt((v1[0] - v2[0])**2 + (v1[1] - v2[1])**2 + (v1[2] - v2[2])**2)

def getPathLength(path):
    firstPoint = getCoordFromPathPoint(path.point(0))
    lastPoint = getCoordFromPathPoint(path.point(1))
    return getDistance2D(firstPoint, lastPoint)

def getPixelLoc(pixels, x, y):
    col = list(pixels[int(x), int(y)])
    return (col[0]/255.0, col[1]/255.0, col[2]/255.0)

def loadImage(url):
    img = Image.open(url)
    img = img.convert('RGB')
    return img.load() # pixels

def restoreXY(point):
    x = int(point.co[0] * 255.0)
    y = int(point.co[1] * -255.0)
    if (x < 0):
        x = 0
    elif (x > 255):
        x = 255
    if (y < 0):
        y = 0
    elif (y > 255):
        y = 255
    return (x, y)    

la = Latk(init=True)
paths, attr = svg2paths("test.svg")
pathLimit = 0.05
minPathPoints = 3
epsilon = 0.00005

for path in paths:
    numPoints = getPathLength(path)
    numRange = int(numPoints)
    if (numRange > 1):
        coords = []
        for i in range(numRange):
            pt = path.point(i/(numPoints-1))
            point = getCoordFromPathPoint(pt)
            coord = (point[0]/255.0, point[1]/-255.0, 0)
            if (i == 0):
                coords.append(coord)
            else:
                lastCoord = coords[len(coords)-1]
                if getDistance2D(coord, lastCoord) < pathLimit:
                    coords.append(coord)
                else:
                    coords = rdp(coords, epsilon=epsilon)
                    if (len(coords) >= minPathPoints):
                        la.setCoords(coords)
                    coords = []
                    coords.append(coord)
        coords = rdp(coords, epsilon=epsilon)            
        if (len(coords) >= minPathPoints):
            la.setCoords(coords)

img_depth = loadImage("test-depth.png")
img_rgb = loadImage("test-rgb.png")

for layer in la.layers:
    for frame in layer.frames:
        for stroke in frame.strokes:
            firstCoord = restoreXY(stroke.points[0])
            stroke.color = getPixelLoc(img_rgb, firstCoord[0], firstCoord[1])
            for point in stroke.points:
                coord = restoreXY(point)
                depth = getPixelLoc(img_depth, coord[0], coord[1])[0]
                point.co = (point.co[0], point.co[1], depth)

la.write("test.latk")