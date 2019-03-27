import sys
import os
import platform

sys.path.insert(0, './latk.py')
sys.path.insert(1, './pix2pix-tensorflow')

import latk
import pix2pix

osName = platform.system()
autotracePath = "autotrace" # Linux
if (osName == "Windows"):
	autotracePath = "C:\\Program Files\\AutoTrace\\autotrace.exe"
elif (osName == "Mac"):
	autotracePath == "/Applications/AutoTrace.app/Contents/MacOs/AutoTrace"