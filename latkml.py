import sys
sys.path.insert(0, './latk.py')
#sys.path.insert(1, './pix2pix-tensorflow')

import platform
osName = platform.system()

import os
from latk import *
from svgpathtools import *  # https://github.com/mathandy/svgpathtools
from PIL import Image # https://gist.github.com/n1ckfg/58b5425a1b81aa3c60c3d3af7703eb3b


# *** Step 1/5: Extract frames from source movie with ffmpeg. ***
#

# *** Step 2/5: Resize to 512x256 with imagemagick or pil. ***
#

# *** Step 3/5: Process with Pix2pix. ***
#os.system("python ./pix2pix-tensorflow/pix2pix.py --mode test --output_dir ./pix2pix-tensorflow/files/output --input_dir ./pix2pix-tensorflow/files/input --checkpoint ./pix2pix-tensorflow/files/model")


# *** Step 4/5: Convert Pix2pix png output to tga and run Autotrace. ***
at_path = "autotrace" # linux doesn't need path handled
if (osName == "Windows"):
	at_path = "\"C:\\Program Files\\AutoTrace\\autotrace\""
elif (osName == "Darwin"): # Mac
	at_path = "/Applications/autotrace.app/Contents/MacOS/autotrace"

at_bgcolor = "#000000"
at_color = 16
at_error_threshold=10
at_line_threshold=0
at_line_reversion_threshold=10

at_cmd = " -background-color=" + str(at_bgcolor) + " -color=" + str(at_color) + " -centerline -error-threshold=" + str(at_error_threshold) + "-line-threshold=" + str(at_line_threshold) + " -line-reversion-threshold=" + str(at_line_reversion_threshold)

im_path = "convert"
if (osName == "Windows"):
	im_path = "magick"

os.system("cd ./pix2pix-tensorflow/files/output/images")
os.system("rm *.tga")

if (osName == "Windows"):
	os.system("for %%i in (%1\\*-outputs.png) do " + im_path + " %%i -colorspace RGB -colorspace sRGB -depth 8 -alpha off %%~nxi-rgb.png")
	os.system("for %%i in (%1\\*.tga) do " + at_path + at_cmd + " -output=%%~nxi.svg -output-format=svg %%i")
else:
	os.system("for file in *-outputs.png; do " + im_path + " $file $file.tga; done")
	os.system("for file in *.tga; do " + at_path + " $file " + at_cmd + " -output-format=svg -output-file $file.svg; done")

os.system("rm *.tga")




	


os.system(autotraceCmd)


# *** Step 5/5: Create final latk file from svg and image output. ***
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