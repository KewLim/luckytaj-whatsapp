@echo off
echo ========================================
echo Granting WRITE_SECURE_SETTINGS Permission
echo ========================================
echo.
echo This script will grant the required permission to your Android device
echo for Appium automation to work properly.
echo.
echo Device UDID: 8d70d7c0
echo.

REM Check if device is connected
adb -s 8d70d7c0 get-state >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Device 8d70d7c0 is not connected!
    echo Please connect your device and try again.
    pause
    exit /b 1
)

echo [INFO] Device is connected. Proceeding with permission grant...
echo.

REM Grant WRITE_SECURE_SETTINGS permission via adb shell
echo [STEP 1] Attempting to grant WRITE_SECURE_SETTINGS permission...
adb -s 8d70d7c0 shell "pm grant com.android.shell android.permission.WRITE_SECURE_SETTINGS 2>&1 || echo 'Permission grant via pm failed, trying alternative method...'"
echo.

REM Alternative method: Use appops to set the permission
echo [STEP 2] Setting permission via appops...
adb -s 8d70d7c0 shell "appops set com.android.shell WRITE_SETTINGS allow"
echo.

REM Try to set hidden API policy directly (this might work after permission grant)
echo [STEP 3] Attempting to set hidden API policy...
adb -s 8d70d7c0 shell "settings put global hidden_api_policy_pre_p_apps 1 2>&1 || echo 'Settings command still requires system permission'"
adb -s 8d70d7c0 shell "settings put global hidden_api_policy_p_apps 1 2>&1 || echo 'Settings command still requires system permission'"
adb -s 8d70d7c0 shell "settings put global hidden_api_policy 1 2>&1 || echo 'Settings command still requires system permission'"
echo.

echo ========================================
echo Permission Grant Completed
echo ========================================
echo.
echo If you still see permission errors, you may need to:
echo 1. Enable Developer Options on your device
echo 2. Enable USB Debugging
echo 3. Enable "USB debugging (Security settings)" if available
echo 4. On some devices, you need to connect via wireless debugging
echo.
pause
