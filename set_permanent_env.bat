@echo off
echo ===============================================
echo    SETTING PERMANENT ANDROID ENVIRONMENT
echo ===============================================
echo.
echo This will set ANDROID_HOME and ANDROID_SDK_ROOT permanently.
echo.
echo Running PowerShell script...
powershell -ExecutionPolicy Bypass -File "%~dp0set_permanent_env.ps1"
echo.
echo Environment setup complete!
pause