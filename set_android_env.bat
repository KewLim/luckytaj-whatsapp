@echo off
echo ===============================================
echo     SETTING UP ANDROID ENVIRONMENT
echo ===============================================

REM Set Android SDK environment variables for current session
set "ANDROID_HOME=%~dp0android-sdk"
set "ANDROID_SDK_ROOT=%~dp0android-sdk"
set "PATH=%ANDROID_HOME%\platform-tools;%PATH%"

echo ✅ Android SDK Home: %ANDROID_HOME%
echo ✅ Android SDK Root: %ANDROID_SDK_ROOT%
echo ✅ Platform Tools added to PATH
echo.

REM Test ADB
echo Testing ADB connection...
adb version
echo.

echo Environment variables set for this session!
echo You can now use:
echo   - adb devices
echo   - appium server --port 4723
echo   - python whatsapp.py
echo.