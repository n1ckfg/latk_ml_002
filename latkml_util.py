import sys
sys.path.insert(0, './latk.py')
sys.path.insert(1, './kinect_converter.py')

from kinect_converter import *
from latk import *
from PIL import Image # https://gist.github.com/n1ckfg/58b5425a1b81aa3c60c3d3af7703eb3b
from svgpathtools import *  # https://github.com/mathandy/svgpathtools
from math import sqrt
import fnmatch
import os


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

def holoflixToPix2Pix(file, useDepthForContour):
    sourceImgUrl = file
    sourceImg = loadImage(sourceImgUrl)
    sourceLeftImg = newImage(480, 480)
    sourceRightImg = newImage(480, 480)

    if (useDepthForContour == True):
        sourceLeftImg = cropImage(sourceImg, 80, 120, 560, 600)
        sourceRightImg = cropImage(sourceImg, 720, 120, 1200, 600)
    else:
        sourceRightImg = cropImage(sourceImg, 80, 120, 560, 600)
        sourceLeftImg = cropImage(sourceImg, 720, 120, 1200, 600)

    destImg = newImage(960, 480)
    pasteImage(sourceLeftImg, destImg, 0, 0, 480, 480)
    pasteImage(sourceRightImg, destImg, 480, 0, 960, 480)
    saveImage(destImg, sourceImgUrl)

def svgToLatk(finalUrl, camera_type, useDepthForContour, minPathPoints):
    kc = KinectConverter(camera_type)

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
    epsilon = 0.00005
    scaleDepthVals = 0.1

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

                finalPoint = kc.convertDepthToWorld(point.co[0], point.co[1], depth)

                #offset = (0, 0, 0) #kc.maxBitDepth/10.0)
                #point.co = ((-finalPoint[0] + offset[0]) * scaleDepthVals, (finalPoint[2]/10.0 + offset[2]) * scaleDepthVals, (-finalPoint[1] + offset[1]) * scaleDepthVals)
                point.co = (finalPoint[0], finalPoint[2], -finalPoint[1])

        print("Saved frame " + str(counter) + " of " + str(len(filesSvg)))
        counter += 1

    la.normalize(-5, 5)
    la.write(finalUrl)
    print("\n\n*** Wrote latk file. ***\n")