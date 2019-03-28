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

at_color = 16
at_error_threshold=10
at_line_threshold=0
at_line_reversion_threshold=10
autotraceCmd = ""

osName = platform.system()
if (osName == "Windows"):
	autotraceCmd = "\"C:\\Program Files\\AutoTrace\\autotrace\" -background-color=#000000 -color=16 -centerline -error-threshold=10 -line-threshold=0 -line-reversion-threshold=10 -output=%~nx1.svg -output-format=svg %1"
elif (osName == "Darwin"): # Mac
	autotraceCmd = "/Applications/autotrace.app/Contents/MacOS/autotrace -background-color=#000000 -color=16 -centerline -error-threshold=10 -line-threshold=0 -line-reversion-threshold=10 -output=%~nx1.svg -output-format=svg %1"
else: # assume Linux
	autotraceCmd = "autotrace -background-color=#000000 -color=16 -centerline -error-threshold=10 -line-threshold=0 -line-reversion-threshold=10 -output=%~nx1.svg -output-format=svg %1"

os.system(autotraceCmd)