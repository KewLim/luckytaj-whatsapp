# 🔧 Android SDK Environment Setup

## ❌ Problem
Appium Inspector shows: `Neither ANDROID_HOME nor ANDROID_SDK_ROOT environment variable was exported`

## ✅ Solution Options

### **Option 1: Set Permanent Environment Variables (Recommended)**

1. **Run the setup script:**
   ```bash
   set_permanent_env.bat
   ```

2. **Restart these applications:**
   - Close and reopen Appium Inspector
   - Close and reopen any Command Prompt/PowerShell windows
   - Restart any IDEs

3. **Verify the setup:**
   ```powershell
   echo $env:ANDROID_HOME
   echo $env:ANDROID_SDK_ROOT
   ```

### **Option 2: Launch Appium Inspector with Environment (Quick Fix)**

1. **Start Appium Server:**
   ```bash
   run_appium.bat
   ```

2. **Launch Appium Inspector with environment:**
   ```bash
   launch_appium_inspector.bat
   ```

### **Option 3: Manual Environment Check**

Open PowerShell and run:
```powershell
$env:ANDROID_HOME = "C:\Users\BDC Computer ll\Downloads\Appium-test\android-sdk"
$env:ANDROID_SDK_ROOT = "C:\Users\BDC Computer ll\Downloads\Appium-test\android-sdk"
```

Then launch Appium Inspector from the same PowerShell window.

## 🎯 Appium Inspector Settings

**Server URL:** `http://127.0.0.1:4723`

**Desired Capabilities:**
```json
{
  "platformName": "Android",
  "appium:automationName": "UiAutomator2",
  "appium:deviceName": "AndroidDevice",
  "appium:appPackage": "com.whatsapp.w4b",
  "appium:appActivity": "com.whatsapp.home.ui.HomeActivity",
  "appium:noReset": true
}
```

## 🔍 Verify Setup

1. **Check environment variables:**
   ```bash
   echo %ANDROID_HOME%
   echo %ANDROID_SDK_ROOT%
   ```

2. **Test ADB:**
   ```bash
   adb devices
   ```

3. **Test Appium connection in Inspector**

## 🚨 If Still Not Working

1. **Restart your computer** (ensures all applications pick up new environment variables)
2. **Run as Administrator** if permission issues occur
3. **Check Windows Environment Variables manually:**
   - Press `Win + R` → `sysdm.cpl` → Advanced → Environment Variables
   - Look for `ANDROID_HOME` and `ANDROID_SDK_ROOT` in User variables

## 📁 Expected Paths
- **ANDROID_HOME**: `C:\Users\BDC Computer ll\Downloads\Appium-test\android-sdk`
- **ANDROID_SDK_ROOT**: `C:\Users\BDC Computer ll\Downloads\Appium-test\android-sdk`
- **ADB**: `C:\Users\BDC Computer ll\Downloads\Appium-test\android-sdk\platform-tools\adb.exe`