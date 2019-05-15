@echo off

rem https://serverfault.com/questions/95686/change-current-directory-to-the-batch-file-directory
cd /D %~dp0

rem file, fps, use depth for contour
python latkml.py -- %1 2 True

@pause