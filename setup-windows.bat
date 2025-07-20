@echo off
REM Google Cloud Access Tool - Windows Setup Script
REM This script sets up the local environment for running the application on Windows

setlocal enabledelayedexpansion

echo ==========================================
echo Google Cloud Access Tool - Windows Setup
echo ==========================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo [SUCCESS] Python found
python --version

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pip is not available
    echo Please ensure pip is installed with Python
    pause
    exit /b 1
)

echo [SUCCESS] pip found

REM Create virtual environment
echo [INFO] Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo [SUCCESS] Virtual environment created
) else (
    echo [INFO] Virtual environment already exists
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo [INFO] Upgrading pip...
python -m pip install --upgrade pip

REM Install Python dependencies
echo [INFO] Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install Python dependencies
    pause
    exit /b 1
)
echo [SUCCESS] Python dependencies installed

REM Check if Google Cloud SDK is installed
gcloud --version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Google Cloud SDK not found
    echo Please install Google Cloud SDK from:
    echo https://cloud.google.com/sdk/docs/install
    echo.
    echo After installation, run:
    echo gcloud auth application-default login
    echo gcloud config set project YOUR_PROJECT_ID
) else (
    echo [SUCCESS] Google Cloud SDK found
    gcloud --version
    
    REM Check authentication
    gcloud auth list --filter=status:ACTIVE --format="value(account)" >nul 2>&1
    if errorlevel 1 (
        echo [WARNING] Not authenticated with Google Cloud
        echo Please run: gcloud auth application-default login
    ) else (
        echo [SUCCESS] Already authenticated with Google Cloud
    )
    
    REM Check project configuration
    for /f "tokens=*" %%i in ('gcloud config get-value project 2^>nul') do set PROJECT=%%i
    if defined PROJECT (
        echo [SUCCESS] Project configured: !PROJECT!
    ) else (
        echo [WARNING] No project configured
        echo Please run: gcloud config set project YOUR_PROJECT_ID
    )
)

REM Create data directories
echo [INFO] Creating data directories...
if not exist "data" mkdir data
if not exist "logs" mkdir logs
echo [SUCCESS] Data directories created

REM Create environment file
echo [INFO] Creating environment file...
if not exist ".env" (
    (
        echo # Google Cloud Access Tool Environment Variables
        echo GOOGLE_CLOUD_PROJECT=your-project-id
        echo GOOGLE_CLOUD_REGION=us-central1
        echo LOG_LEVEL=INFO
        echo MAX_LOG_ENTRIES=100
        echo REFRESH_INTERVAL=30
    ) > .env
    echo [SUCCESS] .env file created
) else (
    echo [INFO] .env file already exists
)

REM Create run script
echo [INFO] Creating run script...
(
    echo @echo off
    echo REM Google Cloud Access Tool - Windows Run Script
    echo setlocal
    echo.
    echo REM Get script directory
    echo set "SCRIPT_DIR=%%~dp0"
    echo.
    echo REM Activate virtual environment if it exists
    echo if exist "%%SCRIPT_DIR%%venv\Scripts\activate.bat" ^(
    echo     call "%%SCRIPT_DIR%%venv\Scripts\activate.bat"
    echo ^)
    echo.
    echo REM Load environment variables
    echo if exist "%%SCRIPT_DIR%%.env" ^(
    echo     for /f "tokens=1,2 delims==" %%a in ^('%%SCRIPT_DIR%%.env'^) do ^(
    echo         if not "%%a"=="" if not "%%a:~0,1%%"=="#" set "%%a=%%b"
    echo     ^)
    echo ^)
    echo.
    echo REM Run the application
    echo cd /d "%%SCRIPT_DIR%%"
    echo python run.py
    echo.
    echo pause
) > run.bat
echo [SUCCESS] Run script created

REM Create desktop shortcut
echo [INFO] Creating desktop shortcut...
set "DESKTOP=%USERPROFILE%\Desktop"
if exist "%DESKTOP%" (
    (
        echo @echo off
        echo cd /d "%~dp0"
        echo call run.bat
    ) > "%DESKTOP%\Google Cloud Access Tool.bat"
    echo [SUCCESS] Desktop shortcut created
) else (
    echo [WARNING] Desktop directory not found, skipping shortcut creation
)

echo.
echo ==========================================
echo [SUCCESS] Setup completed successfully!
echo ==========================================
echo.
echo Next steps:
echo 1. Authenticate with Google Cloud:
echo    gcloud auth application-default login
echo.
echo 2. Set your project ID:
echo    gcloud config set project YOUR_PROJECT_ID
echo.
echo 3. Run the application:
echo    run.bat
echo    or
echo    python run.py
echo.
echo 4. Or use the desktop shortcut
echo.
pause 