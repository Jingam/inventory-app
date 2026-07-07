@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM Hardened build (best effort):
REM 1) Compile to standalone EXE with Nuitka
REM 2) Data file encryption key provided by INVENTORY_DATA_KEY

cd /d "%~dp0"

set "ENTRY=main.py"
set "APP_NAME=inventory-app"
set "BUILD_ROOT=.hardened_build"
set "DIST_DIR=dist"

if not exist "%ENTRY%" (
    echo [ERROR] Entry file not found: %ENTRY%
    exit /b 1
)

set "PY_CMD="
if exist ".venv\Scripts\python.exe" (
    set "PY_CMD=.venv\Scripts\python.exe"
) else (
    where python >nul 2>nul
    if not errorlevel 1 (
        set "PY_CMD=python"
    ) else (
        where py >nul 2>nul
        if not errorlevel 1 (
            set "PY_CMD=py -3"
        )
    )
)

if "%PY_CMD%"=="" (
    echo [ERROR] Could not find Python interpreter.
    echo Install Python or create .venv, then rerun.
    exit /b 1
)

echo [INFO] Using Python command: %PY_CMD%

if "%INVENTORY_DATA_KEY%"=="" (
    set /p INVENTORY_DATA_KEY=Enter INVENTORY_DATA_KEY for encrypted JSON access: 
)

if "%INVENTORY_DATA_KEY%"=="" (
    echo [ERROR] INVENTORY_DATA_KEY cannot be empty.
    exit /b 1
)

echo.
echo [1/7] Installing build dependencies...
%PY_CMD% -m pip install --upgrade pip
if errorlevel 1 goto :fail
%PY_CMD% -m pip install --upgrade nuitka ordered-set zstandard
if errorlevel 1 goto :fail

echo.
echo [2/7] Cleaning old artifacts...
if exist "%BUILD_ROOT%" rmdir /s /q "%BUILD_ROOT%"
if exist "%DIST_DIR%\%APP_NAME%.exe" del /q "%DIST_DIR%\%APP_NAME%.exe"

echo.
echo [3/7] Compiling with Nuitka...
set "NUITKA_FLAGS=--onefile --standalone --windows-console-mode=force --assume-yes-for-downloads --output-dir=%DIST_DIR% --output-filename=%APP_NAME%.exe"
%PY_CMD% -m nuitka %NUITKA_FLAGS% "%ENTRY%"
if errorlevel 1 goto :fail

echo.
echo [4/7] Writing launch helper that injects key at runtime...
(
  echo @echo off
  echo setlocal
  echo if "%%INVENTORY_DATA_KEY%%"=="" set /p INVENTORY_DATA_KEY=Enter INVENTORY_DATA_KEY: 
  echo if "%%INVENTORY_DATA_KEY%%"=="" ^(
  echo   echo [ERROR] INVENTORY_DATA_KEY is required.
  echo   exit /b 1
  echo ^)
  echo "%%~dp0%APP_NAME%.exe"
) > "%DIST_DIR%\run-%APP_NAME%.bat"
if errorlevel 1 goto :fail

echo.
echo [5/7] Cleaning temporary build folders...
if exist "%BUILD_ROOT%" rmdir /s /q "%BUILD_ROOT%"
if exist "%DIST_DIR%\%APP_NAME%.build" rmdir /s /q "%DIST_DIR%\%APP_NAME%.build"
if exist "%DIST_DIR%\%APP_NAME%.onefile-build" rmdir /s /q "%DIST_DIR%\%APP_NAME%.onefile-build"

echo.
echo [6/7] Done.
echo Output EXE: %DIST_DIR%\%APP_NAME%.exe
echo Launcher:   %DIST_DIR%\run-%APP_NAME%.bat
echo.
echo IMPORTANT:
echo - Keep INVENTORY_DATA_KEY secret and stable for existing data files.
echo - Losing/changing key means encrypted JSON cannot be decrypted.
echo - This is strong best-effort hardening, not absolute anti-reverse-engineering.
exit /b 0

:fail
echo.
echo [ERROR] Build failed. Fix the errors above and rerun.
exit /b 1
