import sys
sys.path.insert(0, './latkml_util.py')

argv = sys.argv
argv = argv[argv.index("--") + 1:]  # get all args after "--"
camera_type = str(argv[0])
useDepthForContour = bool(argv[1])
minPathPoints = int(argv[2]) # 3

import os
from latkml_util import *

os.chdir("./pix2pix-tensorflow/files/output/images")

svgToLatk("../../../../output.latk", camera_type, useDepthForContour, minPathPoints)