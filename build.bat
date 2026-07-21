@echo off
echo =========================================
echo    PCCSIM Packaging Script (PyInstaller)
echo =========================================

echo.
echo [1] Cleaning previous build folders...
if exist build (
    rmdir /s /q build
    echo build folder removed.
)
if exist dist (
    rmdir /s /q dist
    echo dist folder removed.
)

echo.
echo [2] Running PyInstaller to build the executable...
pyinstaller --clean PCCIM.spec

echo.
if %errorlevel% neq 0 (
    echo [!] Build failed! Please check the errors above.
) else (
    echo [3] Build finished successfully! You can find the executable in the 'dist\PCCIM' folder.
)

echo.
pause
