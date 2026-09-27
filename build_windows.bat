@echo off
setlocal
cd /d "%~dp0"

python -m pip install -r requirements-build.txt
if errorlevel 1 exit /b 1

python -m PyInstaller --noconfirm --clean --windowed --onefile --icon="%~dp0assets\BAD_Save_Switch.ico" --add-data "%~dp0assets\BAD_Save_Switch.ico;assets" --name BAD-SaveSwitch --distpath dist --workpath build\pyinstaller --specpath build main.py
if errorlevel 1 exit /b 1

echo.
echo Built dist\BAD-SaveSwitch.exe
endlocal