@echo off
pushd %~dp0
echo Installing PyInstaller...
pip install pyinstaller

echo Converting Icon...
python convert_icon.py

echo Building EXE...
python -m PyInstaller --clean --noconsole --onefile --icon="folder.ico" --name "Agalar911_Autoclicker" src/main.py

echo Build Complete! Check the 'dist' folder.
pause
