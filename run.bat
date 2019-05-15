@echo off

rem https://serverfault.com/questions/95686/change-current-directory-to-the-batch-file-directory
cd /D %~dp0

rem file, fps, use depth for contour, colors, error threshold, line threshold, line reversion threshold
python latkml.py -- %1 1 False 3 100 10 20

@pause