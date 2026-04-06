@echo off
REM =========================================================================
REM Mindful Organizer - Windows Build Script
REM =========================================================================
REM This script builds the Mindful Organizer application for Windows.
REM It creates a virtual environment, installs dependencies, runs PyInstaller,
REM and prepares the distribution folder.
REM
REM Usage:
REM   build_windows.bat
REM
REM Prerequisites:
REM   - Python 3.9 or later installed and available on PATH
REM   - Internet connection (for downloading dependencies)
REM =========================================================================

setlocal enabledelayedexpansion

set "PROJECT_ROOT=%~dp0"
set "VENV_DIR=%PROJECT_ROOT%venv_build"
set "DIST_DIR=%PROJECT_ROOT%dist"
set "SPEC_FILE=%PROJECT_ROOT%mindful_organizer.spec"
set "REQUIRED_PYTHON_MAJOR=3"
set "REQUIRED_PYTHON_MINOR=9"

echo.
echo ================================================================
echo   Mindful Organizer - Windows Build
echo ================================================================
echo.

REM -----------------------------------------------------------------------
REM Step 1: Check Python version
REM -----------------------------------------------------------------------
echo [Step 1/6] Checking Python installation...

where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: Python is not installed or not on PATH.
    echo Please install Python %REQUIRED_PYTHON_MAJOR%.%REQUIRED_PYTHON_MINOR%+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    exit /b 1
)

REM Parse Python version
for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%v"
for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do (
    set "PY_MAJOR=%%a"
    set "PY_MINOR=%%b"
)

echo Found Python %PYTHON_VERSION%

if %PY_MAJOR% lss %REQUIRED_PYTHON_MAJOR% (
    echo ERROR: Python %REQUIRED_PYTHON_MAJOR%.%REQUIRED_PYTHON_MINOR%+ is required. Found %PYTHON_VERSION%.
    exit /b 1
)
if %PY_MAJOR% equ %REQUIRED_PYTHON_MAJOR% (
    if %PY_MINOR% lss %REQUIRED_PYTHON_MINOR% (
        echo ERROR: Python %REQUIRED_PYTHON_MAJOR%.%REQUIRED_PYTHON_MINOR%+ is required. Found %PYTHON_VERSION%.
        exit /b 1
    )
)

echo Python version OK.
echo.

REM -----------------------------------------------------------------------
REM Step 2: Create virtual environment
REM -----------------------------------------------------------------------
echo [Step 2/6] Setting up virtual environment...

if exist "%VENV_DIR%" (
    echo Removing existing build virtual environment...
    rmdir /s /q "%VENV_DIR%"
)

python -m venv "%VENV_DIR%"
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to create virtual environment.
    exit /b 1
)

REM Activate the virtual environment
call "%VENV_DIR%\Scripts\activate.bat"
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to activate virtual environment.
    exit /b 1
)

echo Virtual environment created and activated.
echo.

REM -----------------------------------------------------------------------
REM Step 3: Install dependencies
REM -----------------------------------------------------------------------
echo [Step 3/6] Installing dependencies...

REM Upgrade pip first
python -m pip install --upgrade pip >nul 2>&1

REM Install project dependencies
echo Installing project requirements...
pip install -r "%PROJECT_ROOT%requirements.txt"
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to install project dependencies.
    echo Check requirements.txt and your internet connection.
    exit /b 1
)

REM Install PyQt6 (may not be in requirements.txt if it is a desktop-only dep)
echo Installing PyQt6...
pip install PyQt6
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to install PyQt6.
    exit /b 1
)

REM Install PyInstaller
echo Installing PyInstaller...
pip install pyinstaller
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to install PyInstaller.
    exit /b 1
)

echo All dependencies installed.
echo.

REM -----------------------------------------------------------------------
REM Step 4: Run PyInstaller
REM -----------------------------------------------------------------------
echo [Step 4/6] Building application with PyInstaller...

if not exist "%SPEC_FILE%" (
    echo ERROR: Spec file not found at %SPEC_FILE%
    exit /b 1
)

REM Clean previous builds
if exist "%PROJECT_ROOT%build" (
    echo Cleaning previous build directory...
    rmdir /s /q "%PROJECT_ROOT%build"
)
if exist "%DIST_DIR%\MindfulOrganizer" (
    echo Cleaning previous dist output...
    rmdir /s /q "%DIST_DIR%\MindfulOrganizer"
)

pyinstaller --clean --noconfirm "%SPEC_FILE%"
if %ERRORLEVEL% neq 0 (
    echo ERROR: PyInstaller build failed.
    echo Review the output above for details.
    exit /b 1
)

echo PyInstaller build completed.
echo.

REM -----------------------------------------------------------------------
REM Step 5: Create distribution folder
REM -----------------------------------------------------------------------
echo [Step 5/6] Preparing distribution folder...

set "RELEASE_DIR=%DIST_DIR%\MindfulOrganizer-Release"

if exist "%RELEASE_DIR%" (
    rmdir /s /q "%RELEASE_DIR%"
)
mkdir "%RELEASE_DIR%"

REM Copy the built application
xcopy /e /i /q "%DIST_DIR%\MindfulOrganizer" "%RELEASE_DIR%\MindfulOrganizer"

REM Copy the privacy policy
if exist "%PROJECT_ROOT%windows_store\privacy_policy.html" (
    copy /y "%PROJECT_ROOT%windows_store\privacy_policy.html" "%RELEASE_DIR%\" >nul
)

REM Copy the license
if exist "%PROJECT_ROOT%LICENSE" (
    copy /y "%PROJECT_ROOT%LICENSE" "%RELEASE_DIR%\" >nul
)

echo Distribution folder prepared at: %RELEASE_DIR%
echo.

REM -----------------------------------------------------------------------
REM Step 6: Summary and next steps
REM -----------------------------------------------------------------------
echo [Step 6/6] Build complete!
echo.
echo ================================================================
echo   BUILD SUMMARY
echo ================================================================
echo.
echo   Application:   %DIST_DIR%\MindfulOrganizer\mindful-organizer.exe
echo   Distribution:  %RELEASE_DIR%
echo.
echo ================================================================
echo   NEXT STEPS FOR MSIX PACKAGING
echo ================================================================
echo.
echo   To create an MSIX package for the Windows Store:
echo.
echo   1. Ensure all visual assets are in windows_store\assets\
echo      (see windows_store\assets\README.md for requirements)
echo.
echo   2. Install the Windows 10 SDK (10.0.22621.0 or later)
echo      from Visual Studio Installer or:
echo      https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/
echo.
echo   3. Run the MSIX build script from PowerShell:
echo      cd windows_store
echo      .\build_msix.ps1 -SkipBuild
echo.
echo   4. To sign the package (required for distribution):
echo      .\build_msix.ps1 -SkipBuild -Sign -CertPath path\to\cert.pfx
echo.
echo   5. To validate before Store submission:
echo      .\build_msix.ps1 -SkipBuild -Validate
echo.
echo   6. Submit the signed .msix to Partner Center:
echo      https://partner.microsoft.com/dashboard
echo.
echo ================================================================
echo.

REM Deactivate virtual environment
call deactivate

echo Done.
exit /b 0
