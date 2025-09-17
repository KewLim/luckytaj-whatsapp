@echo off
title Appium Server with Android SDK
echo ===============================================
echo    STARTING APPIUM WITH ANDROID SDK SETUP
echo ===============================================

REM Set Android SDK environment variables
set "ANDROID_HOME=%~dp0android-sdk"
set "ANDROID_SDK_ROOT=%~dp0android-sdk"
set "PATH=%ANDROID_HOME%\platform-tools;%PATH%"

echo Android SDK Home: %ANDROID_HOME%
echo Android SDK Root: %ANDROID_SDK_ROOT%
echo.
echo Starting Appium Server on port 4723...
echo Press Ctrl+C to stop the server
echo.

appium server --port 4723 --log-level info