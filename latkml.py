import sys
sys.path.insert(0, './latkml_util.py')

argv = sys.argv
argv = argv[argv.index("--") + 1:]  # get all args after "--"
input_video = str(argv[0])
camera_type = str(argv[1])
input_fps = int(argv[2])
useDepthForContour = bool(argv[3])
minPathPoints = int(argv[4]) # 3

import platform
osName = platform.system()

import os
import fnmatch
from latkml_util import *

# https://www.linux.com/news/making-vector-graphics-out-bitmaps-frontline-and-autotrace
'''
Color count -- When set to zero, Autotrace will trace out separate regions for every color 
that it finds. If you image has a lot of colors (as a photograph or a scanned image might) 
you can tell Autotrace to reduce the palette to as few colors as you want.
'''
at_color = int(argv[5]) # 16

'''
Error Threshold -- Autotrace first finds edges in the bitmapped image, then tries to fit 
them together into shapes. The error threshold determines how many pixels a curve may be 
off by and still be joined with its neighbors into a shape.
'''
at_error_threshold = int(argv[6]) # 10

'''
Line Threshold -- Whenever Autotrace finds a spline curve, it compares it to the straight 
line you would get by connecting its two endpoints. If the spline is within the line 
threshold value of the straight line, Autotrace will simplify it to a line segment.
'''
at_line_threshold = int(argv[7]) # 0

'''
Line Reversion Threshold -- This setting attempts to do the same thing as Line Threshold: 
reduce nearly-straight spline curves to simpler lines. But whereas Line Threshold simply 
judges the distance between the curve and its straight line, Line Reversion Threshold 
weights this measurement by the length of the spline.
'''
at_line_reversion_threshold = int(argv[8]) # 10

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
    holoflixToPix2Pix(file, useDepthForContour)
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

svgToLatk("../../../../output.latk", camera_type, useDepthForContour, minPathPoints)