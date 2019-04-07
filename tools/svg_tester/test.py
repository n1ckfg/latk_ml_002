from svgpathtools import *
from latk import *

def getCoordFromPathPoint(pt):
    point = str(pt)
    point = point.replace("j","")
    point = point.replace("(","")
    point = point.replace(")","")
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

la = Latk(init=True)
paths, attr = svg2paths("test.svg")

for path in paths:
    numPoints = getPathLength(path)
    numRange = int(numPoints)
    if (numRange > 1):
        coords = []
        for i in range(numRange):
            pt = path.point(i/(numPoints-1))
            point = getCoordFromPathPoint(pt)
            coords.append((point[0]/100.0, point[1]/100.0, 0))
        la.setCoords(coords)

la.clean(epsilon=0.0001)
la.write("test.latk")