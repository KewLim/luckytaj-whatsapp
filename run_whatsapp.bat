@echo off
title WhatsApp Automation with Android SDK
echo ===============================================
echo   WHATSAPP AUTOMATION WITH ANDROID SDK SETUP
echo ===============================================

REM Set Android SDK environment variables
set "ANDROID_HOME=%~dp0android-sdk"
set "ANDROID_SDK_ROOT=%~dp0android-sdk"
set "PATH=%ANDROID_HOME%\platform-tools;%PATH%"

echo Android SDK Home: %ANDROID_HOME%
echo Android SDK Root: %ANDROID_SDK_ROOT%
echo.
echo Starting WhatsApp automation...
echo.

python whatsapp.py

echo.
echo Automation completed. Press any key to exit.
pause