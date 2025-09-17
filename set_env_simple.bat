@echo off
echo ===============================================
echo    SETTING PERMANENT ANDROID ENVIRONMENT
echo ===============================================
echo.

REM Get current directory
set "CURRENT_DIR=%~dp0"
set "ANDROID_SDK_PATH=%CURRENT_DIR%android-sdk"

echo Setting Android SDK environment variables...
echo Android SDK Path: %ANDROID_SDK_PATH%
echo.

REM Set ANDROID_HOME for current user
setx ANDROID_HOME "%ANDROID_SDK_PATH%"
if %errorlevel%==0 (
    echo ✅ ANDROID_HOME set successfully
) else (
    echo ❌ Failed to set ANDROID_HOME
)

REM Set ANDROID_SDK_ROOT for current user
setx ANDROID_SDK_ROOT "%ANDROID_SDK_PATH%"
if %errorlevel%==0 (
    echo ✅ ANDROID_SDK_ROOT set successfully
) else (
    echo ❌ Failed to set ANDROID_SDK_ROOT
)

REM Add platform-tools to PATH
set "PLATFORM_TOOLS_PATH=%ANDROID_SDK_PATH%\platform-tools"
setx PATH "%PATH%;%PLATFORM_TOOLS_PATH%"
if %errorlevel%==0 (
    echo ✅ Platform-tools added to PATH
) else (
    echo ❌ Failed to add platform-tools to PATH
)

echo.
echo 🎉 Environment variables set successfully!
echo.
echo IMPORTANT: You need to restart the following for changes to take effect:
echo 1. Close and reopen any Command Prompt/PowerShell windows
echo 2. Close and reopen Appium Inspector
echo 3. Restart any IDEs or development tools
echo.
echo After restarting, you can verify with:
echo echo %%ANDROID_HOME%%
echo echo %%ANDROID_SDK_ROOT%%
echo.
echo Press any key to continue...
pause >nul