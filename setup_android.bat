@echo off
title Android Setup Helper
echo ===============================================
echo       ANDROID SETUP HELPER
echo ===============================================
echo.
echo This will help you set up your Android device for automation.
echo.
echo STEP 1: Check ADB Connection
echo ===============================================
echo Testing ADB connection...
call "%~dp0platform-tools\adb.exe" version
echo.
echo Checking connected devices...
call "%~dp0platform-tools\adb.exe" devices
echo.
echo ===============================================
echo STEP 2: Device Setup Instructions
echo ===============================================
echo 1. Enable Developer Options:
echo    - Go to Settings ^> About Phone
echo    - Tap "Build Number" 7 times
echo.
echo 2. Enable USB Debugging:
echo    - Go to Settings ^> Developer Options
echo    - Turn ON "USB Debugging"
echo    - Turn ON "Stay Awake" (recommended)
echo.
echo 3. Connect your phone via USB cable
echo.
echo 4. When popup appears on phone, tap "Allow USB Debugging"
echo.
echo ===============================================
echo STEP 3: Test Connection
echo ===============================================
echo Run this command to test: adb devices
echo You should see your device listed.
echo.
pause