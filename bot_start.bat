@echo off

set "base_dir=%~dp0"

cd %base_dir%env\Scripts

call activate

cd ..
cd ..

call python main.py