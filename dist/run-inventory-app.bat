@echo off
setlocal
if "%INVENTORY_DATA_KEY%"=="" set /p INVENTORY_DATA_KEY=Enter INVENTORY_DATA_KEY: 
if "%INVENTORY_DATA_KEY%"=="" (
  echo [ERROR] INVENTORY_DATA_KEY is required.
  exit /b 1
)
"%~dp0inventory-app.exe"
