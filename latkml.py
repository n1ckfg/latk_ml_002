import sys
sys.path.insert(0, './latk.py')
#sys.path.insert(1, './pix2pix-tensorflow')
argv = sys.argv
argv = argv[argv.index("--") + 1:]  # get all args after "--"
input_video = str(argv[0])
input_fps = int(argv[1])
useDepthForContour = bool(argv[2])

import platform
osName = platform.system()

import os
import fnmatch
from latk import *
from svgpathtools import *  # https://github.com/mathandy/svgpathtools
from PIL import Image # https://gist.github.com/n1ckfg/58b5425a1b81aa3c60c3d3af7703eb3b

# https://www.linux.com/news/making-vector-graphics-out-bitmaps-frontline-and-autotrace
'''
Color count -- When set to zero, Autotrace will trace out separate regions for every color 
that it finds. If you image has a lot of colors (as a photograph or a scanned image might) 
you can tell Autotrace to reduce the palette to as few colors as you want.
'''
at_color = int(argv[3]) # 16

'''
Error Threshold -- Autotrace first finds edges in the bitmapped image, then tries to fit 
them together into shapes. The error threshold determines how many pixels a curve may be 
off by and still be joined with its neighbors into a shape.
'''
at_error_threshold = int(argv[4]) # 10

'''
Line Threshold -- Whenever Autotrace finds a spline curve, it compares it to the straight 
line you would get by connecting its two endpoints. If the spline is within the line 
threshold value of the straight line, Autotrace will simplify it to a line segment.
'''
at_line_threshold = int(argv[5]) # 0

'''
Line Reversion Threshold -- This setting attempts to do the same thing as Line Threshold: 
reduce nearly-straight spline curves to simpler lines. But whereas Line Threshold simply 
judges the distance between the curve and its straight line, Line Reversion Threshold 
weights this measurement by the length of the spline.
'''
at_line_reversion_threshold = int(argv[6]) # 10

def getCoordFromPathPoint(pt):
    point = str(pt)
    point = point.replace("(", "")
    point = point.replace("j)", "")
    point = point.split("+")

    x = 0
    y = 0

    try:
        point[0] = point[0].replace("j", "")
        x = float(point[0])
    except:
        pass
    try:
        point[1] = point[1].replace("j", "")
        y = float(point[1])
    except:
        pass

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
    return img

def loadPixels(img):
    return img.load()

def saveImage(img, url): # https://stackoverflow.com/questions/14452824/how-can-i-save-an-image-with-pil
    img.save(url)

def newImage(width, height):
    return Image.new('RGB', (width, height))

def cropImage(img, x1, y1, x2, y2):
    box = (x1, y1, x2, y2)
    return img.crop(box)

def scaleImage(img, w, h):
    return img.resize((w, h), Image.ANTIALIAS)

def pasteImage(source, dest, x1, y1, x2, y2):
    box = (x1, y1, x2, y2)
    dest.paste(source, box)

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


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
at_path = "autotrace" # linux doesn't need path handled
ff_path = "ffmpeg"
if (osName == "Windows"):
    at_path = "\"C:\\Program Files\\AutoTrace\\autotrace\""
    ff_path = "\"C:\\Util\\ffmpeg\\bin\\ffmpeg\""
elif (osName == "Darwin"): # Mac
    at_path = "/Applications/autotrace.app/Contents/MacOS/autotrace"


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
print("\n\n*** Step 1/5: Extract frames from source movie with ffmpeg. ***\n")
try:
    os.makedirs("./pix2pix-tensorflow/files/input")
except:
    print("Input directory already exists.")
try:
    os.makedirs("./pix2pix-tensorflow/files/output")
except:
    print("Output directory already exists.")

os.chdir("./pix2pix-tensorflow/files/input")
if (osName == "Windows"):
    os.system("del *.png")
    os.system("del *.tga")
    os.system("del *.svg")
else:
    os.system("rm *.png")
    os.system("rm *.tga")
    os.system("rm *.svg")
os.chdir("../output/images")
if (osName == "Windows"):
    os.system("del *.png")
    os.system("del *.tga")
    os.system("del *.svg")
else:
    os.system("rm *.png")
    os.system("rm *.tga")
    os.system("rm *.svg")
os.chdir("../../input")

os.system(ff_path + " -i " + input_video + " -vf fps=" + str(input_fps) + " image-%05d.png")
files = fnmatch.filter(os.listdir("."), "*.png")

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
print("\n\n*** Step 2/5: Resize to 512x256 with pil. ***\n")
# https://code-maven.com/listing-a-directory-using-python
for i, file in enumerate(files):
    sourceImgUrl = file
    sourceImg = loadImage(sourceImgUrl)
    sourceLeftImg = None
    sourceRightImg = None

    if (useDepthForContour == True):
        sourceLeftImg = cropImage(sourceImg, 80, 120, 560, 600)
        sourceRightImg = cropImage(sourceImg, 720, 120, 1200, 600)
    else:
        sourceRightImg = cropImage(sourceImg, 80, 120, 560, 600)
        sourceLeftImg = cropImage(sourceImg, 720, 120, 1200, 600)

    sourceLeftImg = scaleImage(sourceLeftImg, 256, 256)
    sourceRightImg = scaleImage(sourceRightImg, 256, 256)
    destImg = newImage(512, 256)
    pasteImage(sourceLeftImg, destImg, 0, 0, 256, 256)
    pasteImage(sourceRightImg, destImg, 256, 0, 512, 256)
    saveImage(destImg, sourceImgUrl)
    print("Saved image " + str(i+1) + " of " + str(len(files)))


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
print("\n\n*** Step 3/5: Process with Pix2pix. ***\n")
os.chdir("../..")
os.system("python pix2pix.py --mode test --output_dir files/output --input_dir files/input --checkpoint files/model")


# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
print("\n\n*** Step 4/5: Convert Pix2pix png output to tga and run Autotrace. ***\n")
at_bgcolor = "#000000"
at_cmd = " -background-color=" + str(at_bgcolor) + " -color=" + str(at_color) + " -centerline -error-threshold=" + str(at_error_threshold) + "-line-threshold=" + str(at_line_threshold) + " -line-reversion-threshold=" + str(at_line_reversion_threshold)

os.chdir("files/output/images")

if (osName == "Windows"):
    os.system("del *.tga")
    try:
        os.system("for %i in (*-outputs.png) do magick %i -colorspace RGB -colorspace sRGB -depth 8 -alpha off %~nxi.tga")
    except:
        print("Encountered an error doing ImageMagick batch.")
    try:
        os.system("for %i in (*.tga) do " + at_path + at_cmd + " -output=%~nxi.svg -output-format=svg %i")
    except:
        print("Encountered an error doing Autotrace batch.")
    os.system("del *.tga")
else:
    os.system("rm *.tga")
    try:
        os.system("for file in *-outputs.png; do convert $file $file.tga; done")
    except:
        print("Encountered an error doing ImageMagick batch.")
    try:
        os.system("for file in *.tga; do " + at_path + " $file " + at_cmd + " -output-format=svg -output-file $file.svg; done")
    except:
        print("Encountered an error doing Autotrace batch.")
    os.system("rm *.tga")
    

# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
print("\n\n*** Step 5/5: Create final latk file from svg and image output. ***\n")
la = Latk(init=False)
la.layers.append(LatkLayer())

# https://code-maven.com/listing-a-directory-using-python
filesSvg = fnmatch.filter(os.listdir("."), "*.svg")

filesRgb = None
filesDepth = None

if (useDepthForContour == True):
    filesRgb = fnmatch.filter(os.listdir("."), "*-targets.png")
    filesDepth = fnmatch.filter(os.listdir("."), "*-inputs.png")
else:
    filesDepth = fnmatch.filter(os.listdir("."), "*-targets.png")
    filesRgb = fnmatch.filter(os.listdir("."), "*-inputs.png")    

pathLimit = 0.05
minPathPoints = 3
epsilon = 0.00005

counter = 1

for i in range(0, len(filesSvg)):
    paths, attr = svg2paths(filesSvg[i])
    img_depth = loadPixels(loadImage(filesDepth[i]))
    img_rgb = loadPixels(loadImage(filesRgb[i]))

    la.layers[0].frames.append(LatkFrame())

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

    for stroke in la.layers[0].frames[len(la.layers[0].frames)-1].strokes:
        firstCoord = restoreXY(stroke.points[0])
        stroke.color = getPixelLoc(img_rgb, firstCoord[0], firstCoord[1])
        for point in stroke.points:
            coord = restoreXY(point)
            depth = getPixelLoc(img_depth, coord[0], coord[1])[0]
            point.co = (-point.co[0]/10.0, depth/10.0, point.co[1]/10.0)

    print("Saved image " + str(counter) + " of " + str(len(filesSvg)))
    counter += 1

finalUrl = "../../../../output.latk"
la.write(finalUrl)
print("\n\n*** Wrote latk file. ***\n")