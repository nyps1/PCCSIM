@echo off
echo ===================================================
echo     PCCSIM Automated PyInstaller Packaging Script
echo ===================================================
echo.

echo [1/4] Cleaning previous build and dist directories...
if exist build (
    rmdir /s /q build
    echo     - Removed build/ directory.
)
if exist dist (
    rmdir /s /q dist
    echo     - Removed dist/ directory.
)

echo.
echo [2/4] Running PyInstaller packaging...
pyinstaller -y --clean PCCIM.spec

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] PyInstaller build failed! Please inspect the logs above.
    pause
    exit /b %errorlevel%
)

echo.
echo [3/4] Copying database and runtime assets to dist\PCCIM\...

if exist pccim.db (
    copy /y pccim.db dist\PCCIM\pccim.db
    echo     - Copied pccim.db to dist\PCCIM\
) else (
    echo     - Warning: pccim.db not found in root. The application will initialize a new database on first launch.
)

if exist ppt_templates (
    xcopy /s /i /y ppt_templates dist\PCCIM\ppt_templates
    echo     - Copied ppt_templates/ to dist\PCCIM\
)

if not exist dist\PCCIM\uploads (
    mkdir dist\PCCIM\uploads
    echo     - Created dist\PCCIM\uploads\
)

if not exist dist\PCCIM\exports (
    mkdir dist\PCCIM\exports
    echo     - Created dist\PCCIM\exports\
)

echo.
echo [4/4] Build Completed Successfully!
echo ===================================================
echo Output Folder: dist\PCCIM\
echo Executable:   dist\PCCIM\PCCIM.exe
echo Database:     dist\PCCIM\pccim.db
echo ===================================================
echo.
pause
