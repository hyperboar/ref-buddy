@echo off
setlocal

REM Set the virtual environment directory
set VENV_DIR=venv

REM Check if Python is installed
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python 3.10 or higher and try again.
    exit /b 1
)

REM Check Python version
python -c "import sys; assert sys.version_info >= (3, 10), 'Python 3.10 or higher is required'; print('Python version check passed.')"

REM Check if virtual environment exists
if not exist %VENV_DIR% (
    echo Creating virtual environment...
    python -m venv %VENV_DIR%
)

REM Activate the virtual environment
call %VENV_DIR%\Scripts\activate

REM Install required packages
echo Installing required packages...
pip install -r requirements.txt

REM Run the main.py script
python main.py

REM Deactivate the virtual environment
deactivate

endlocal