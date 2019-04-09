@echo off

git submodule init
git submodule update --init --recursive
git submodule sync
git submodule foreach git checkout master
git submodule foreach git reset --hard
git submodule foreach git pull origin master

rem NOTE install autotrace manually
rem NOTE install imagemagick manually
rem NOTE install ffmpeg manually

rem cd build
rem build

echo "* Install autotrace manually *"

@pause