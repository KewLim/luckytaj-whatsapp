@echo off
title Appium Server with Android SDK Environment
echo ===============================================
echo   STARTING APPIUM WITH ANDROID SDK ENVIRONMENT
echo ===============================================
echo.

REM Set Android SDK environment variables for this session
set "ANDROID_HOME=%~dp0android-sdk"
set "ANDROID_SDK_ROOT=%~dp0android-sdk"
set "PATH=%ANDROID_HOME%\platform-tools;%PATH%"

echo ✅ ANDROID_HOME: %ANDROID_HOME%
echo ✅ ANDROID_SDK_ROOT: %ANDROID_SDK_ROOT%
echo ✅ Platform-tools in PATH
echo.

REM Verify ADB is working
echo Testing ADB connection...
"%ANDROID_HOME%\platform-tools\adb.exe" version
echo.

REM Start Appium server with environment variables
echo Starting Appium Server on port 4723...
echo Server URL: http://127.0.0.1:4723
echo.
echo ⚠️  IMPORTANT: Keep this window open while using Appium Inspector
echo Press Ctrl+C to stop the server
echo.

appium server --port 4723 --log-level info