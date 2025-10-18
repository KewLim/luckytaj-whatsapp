#!/usr/bin/env python3

from appium.webdriver.webdriver import WebDriver
from appium.options.android.uiautomator2.base import UiAutomator2Options

def quick_test():
    print("🔧 Quick connection test...")

    try:
        options = UiAutomator2Options()
        options.platform_name = "Android"
        options.device_name = "Android Device"
        options.automation_name = "UiAutomator2"
        options.app_package = "com.whatsapp.w4b"
        options.app_activity = "com.whatsapp.home.ui.HomeActivity"
        options.no_reset = True
        options.new_command_timeout = 30

        print("📱 Connecting to device...")
        driver = WebDriver("http://localhost:4723", options=options)

        print("✅ Connected successfully!")
        print("📏 Screen size:", driver.get_window_size())

        driver.quit()
        print("✅ Test completed!")

    except Exception as e:
        print("❌ Failed:", str(e))

if __name__ == "__main__":
    quick_test()