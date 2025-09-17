# 🚀 WhatsApp Automation Setup Guide

## 📋 Prerequisites Installed ✅
- ✅ **Node.js** (v22.19.0)
- ✅ **npm** (v10.9.3)
- ✅ **Appium Server** (v3.0.2)
- ✅ **UiAutomator2 Driver** (v5.0.2)
- ✅ **Android Platform Tools** (ADB v1.0.41)
- ✅ **Python Appium Client** (5.2.4)

## 🔧 Quick Start

### 1. Setup Android Device
Run the setup helper:
```bash
setup_android.bat
```

**Manual Steps:**
1. **Enable Developer Options:**
   - Go to Settings > About Phone
   - Tap "Build Number" 7 times

2. **Enable USB Debugging:**
   - Go to Settings > Developer Options
   - Turn ON "USB Debugging"
   - Turn ON "Stay Awake" (recommended)

3. **Connect via USB and allow debugging**

### 2. Test Device Connection
```bash
adb devices
```
You should see your device listed.

### 3. Start Appium Server (with Android SDK)
```bash
run_appium.bat
```
Or manually with environment setup:
```bash
set_android_env.bat
appium server --port 4723
```

### 4. Configure Your Messages
- Edit `txt/daily_message.txt` - Set your daily message
- Edit `txt/chat_name.txt` - Add/remove chat names (1220 entries loaded)
- Add photo to `daily_photos/` folder (optional)

### 5. Run WhatsApp Automation
```bash
run_whatsapp.bat
```
Or manually:
```bash
set_android_env.bat
python whatsapp.py
```

## 📁 Project Structure
```
📂 Appium-test/
├── 📂 platform-tools/          # Android ADB tools
├── 📂 txt/                     # Text files
│   ├── 📄 chat_name.txt        # Target chats (1220 entries)
│   ├── 📄 daily_message.txt    # Message to send
│   └── 📄 processed_chats_*.txt # Daily logs
├── 📂 daily_photos/            # Photos to send
├── 📄 whatsapp.py              # Main automation script
├── 📄 start_appium.bat         # Start Appium server
├── 📄 setup_android.bat        # Android setup helper
└── 📄 adb.bat                  # ADB wrapper
```

## 🎯 Interactive Menu Features
- Process all 1220 chats
- Start from specific row
- Process specific range
- Process first N entries

## 🔧 Available Commands
```bash
# Test ADB connection
adb devices

# Start Appium server
start_appium.bat

# Setup Android device
setup_android.bat

# Run automation
python whatsapp.py
```

## 🚨 Troubleshooting
- **Device not detected:** Check USB debugging is enabled
- **Appium connection failed:** Make sure server is running on port 4723
- **Permission denied:** Allow USB debugging on device
- **App not found:** Install WhatsApp Business on device

## 📱 Supported Apps
- WhatsApp Business (com.whatsapp.w4b)
- Regular WhatsApp (com.whatsapp) - can be configured

Your automation environment is ready! 🎉