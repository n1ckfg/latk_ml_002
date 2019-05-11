import sys
import os
import platform

sys.path.insert(0, './latk.py')
#sys.path.insert(1, './pix2pix-tensorflow')

from latk import *
#import pix2pix
from svgpathtools import *  # https://github.com/mathandy/svgpathtools
from PIL import Image # https://gist.github.com/n1ckfg/58b5425a1b81aa3c60c3d3af7703eb3b

# 1. PIX2PIX
'''
python pix2pix.py \
  --mode test \
  --output_dir files/output \
  --input_dir files/input \
  --checkpoint files/model

cd files/output/images
rm *.tga
for file in *-outputs.png; do convert $file $file.tga; done
for file in *.tga; do autotrace $file -background-color=000000 -color=16 -centerline -error-threshold=10 -line-threshold=0 -line-reversion-threshold=10 -output-format=svg -output-file $file.svg; done
rm *.tga

'''

# 2. AUTOTRACE
at_path = "autotrace"
at_bgcolor = "#000000"
at_color = 16
at_error_threshold=10
at_line_threshold=0
at_line_reversion_threshold=10
autotraceCmd = ""

at_input_file="test.svg"
at_output_file="output.svg"

osName = platform.system()

if (osName == "Windows"):
	at_path = "\"C:\\Program Files\\AutoTrace\\autotrace\""
elif (osName == "Darwin"): # Mac
	at_path = "/Applications/autotrace.app/Contents/MacOS/autotrace"
	
autotraceCmd = at_path + " -background-color=" + str(at_bgcolor) + " -color=" + str(at_color) + " -centerline -error-threshold=" + str(at_error_threshold) + "-line-threshold=" + str(at_line_threshold) + " -line-reversion-threshold=" + str(at_line_reversion_threshold) + " -output=" + at_output_file + " -output-format=svg " + at_input_file

#os.system(autotraceCmd)

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
                point.co = (-point.co[0]/10.0, depth/10.0, point.co[1]/10.0)

la.write("test.latk")