import sys
import os
import platform

sys.path.insert(0, './latk.py')
sys.path.insert(1, './pix2pix-tensorflow')

import latk
import pix2pix
import PIL.Image as Image # https://gist.github.com/n1ckfg/58b5425a1b81aa3c60c3d3af7703eb3b
import svgpathtools as svg # https://github.com/mathandy/svgpathtools

paths, attributes, svg_attributes = svg.svg2paths2('test.svg')

osName = platform.system()
autotracePath = "autotrace" # Linux
if (osName == "Windows"):
	autotracePath = "C:\\Program Files\\AutoTrace\\autotrace.exe"
elif (osName == "Mac"):
	autotracePath == "/Applications/AutoTrace.app/Contents/MacOs/AutoTrace"
