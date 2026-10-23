@echo off
setlocal
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" goto dependencies
for %%V in (3.12 3.13 3.11 3.10) do (
    py -%%V -c "import sys" >nul 2>&1
    if not errorlevel 1 (
        set "PYCMD=py -%%V"
        goto create_environment
    )
)
python -c "import sys; assert (3,10) <= sys.version_info[:2] <= (3,13)" >nul 2>&1
if not errorlevel 1 (
    set "PYCMD=python"
    goto create_environment
)
echo Python 3.10-3.13 was not found. Install Python 3.12 or 3.13 from python.org.
echo Include the Python launcher and Add Python to PATH, then run this file again.
pause
exit /b 1
:create_environment
%PYCMD% -m venv .venv
if errorlevel 1 (
    echo Could not create the virtual environment. Extract the ZIP to a writable folder first.
    pause
    exit /b 1
)
:dependencies
".venv\Scripts\python.exe" -c "import panda3d; assert panda3d.__version__ == '1.10.16'" >nul 2>&1
if errorlevel 1 (
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 (
        echo Dependency installation failed. Check your internet connection and try again.
        pause
        exit /b 1
    )
)
".venv\Scripts\python.exe" main.py
if errorlevel 1 pause
