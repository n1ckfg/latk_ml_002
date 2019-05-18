@echo off

rem https://serverfault.com/questions/95686/change-current-directory-to-the-batch-file-directory
cd /D %~dp0

rem file, camera type, fps, use depth for contour, min path points, num colors, error threshold, line threshold, line reversion threshold
python test.py -- %1 Structure 1 True 5 2 200 50 50

@pause