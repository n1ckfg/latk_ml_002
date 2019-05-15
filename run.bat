@echo off

rem https://serverfault.com/questions/95686/change-current-directory-to-the-batch-file-directory
cd /D %~dp0

rem file, fps, use depth for contour, min path points, num colors, error threshold, line threshold, line reversion threshold
python latkml.py -- %1 12 True 5 2 200 50 50

@pause