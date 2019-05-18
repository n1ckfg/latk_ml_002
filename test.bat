@echo off

rem https://serverfault.com/questions/95686/change-current-directory-to-the-batch-file-directory
cd /D %~dp0

rem camera type, use depth for contour, min path points
python test.py -- Structure True 5

@pause