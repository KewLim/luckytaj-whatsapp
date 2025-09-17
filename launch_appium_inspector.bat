@echo off
title Launch Appium Inspector with Android SDK
echo ===============================================
echo   LAUNCHING APPIUM INSPECTOR WITH ANDROID SDK
echo ===============================================

REM Set Android SDK environment variables
set "ANDROID_HOME=%~dp0android-sdk"
set "ANDROID_SDK_ROOT=%~dp0android-sdk"
set "PATH=%ANDROID_HOME%\platform-tools;%PATH%"

echo ✅ Android SDK Home: %ANDROID_HOME%
echo ✅ Android SDK Root: %ANDROID_SDK_ROOT%
echo ✅ Platform Tools added to PATH
echo.

echo Starting Appium Inspector...
echo.

REM Try to launch Appium Inspector (common installation paths)
if exist "%LOCALAPPDATA%\Programs\Appium Inspector\Appium Inspector.exe" (
    echo Found Appium Inspector in LocalAppData
    start "" "%LOCALAPPDATA%\Programs\Appium Inspector\Appium Inspector.exe"
) else if exist "%PROGRAMFILES%\Appium Inspector\Appium Inspector.exe" (
    echo Found Appium Inspector in Program Files
    start "" "%PROGRAMFILES%\Appium Inspector\Appium Inspector.exe"
) else if exist "%PROGRAMFILES(X86)%\Appium Inspector\Appium Inspector.exe" (
    echo Found Appium Inspector in Program Files (x86)
    start "" "%PROGRAMFILES(X86)%\Appium Inspector\Appium Inspector.exe"
) else (
    echo ⚠️  Could not find Appium Inspector automatically.
    echo Please manually launch Appium Inspector.
    echo.
    echo The environment variables are now set for this session.
    echo Use Server URL: http://127.0.0.1:4723
)

echo.
echo Environment variables set for Appium Inspector!
pause