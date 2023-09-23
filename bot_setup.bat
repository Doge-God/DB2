call python -m venv env

set "base_dir=%~dp0"

cd %base_dir%env\Scripts

call activate

cd ..
cd ..

call pip install -r requirements.txt

call deactivate