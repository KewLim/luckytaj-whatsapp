#!/usr/bin/env python3

from appium.webdriver.webdriver import WebDriver
from appium.options.android.uiautomator2.base import UiAutomator2Options

def simple_test():
    print("📱 Simple connection test (no app launch)...")

    try:
        options = UiAutomator2Options()
        options.platform_name = "Android"
        options.device_name = "da2a3288"
        options.automation_name = "UiAutomator2"
        options.new_command_timeout = 30

        print("🔌 Connecting to device...")
        driver = WebDriver("http://localhost:4723", options=options)

        print("✅ Connected!")
        size = driver.get_window_size()
        print(f"📏 Screen: {size['width']}x{size['height']}")

        # Try to activate WhatsApp Business
        print("📱 Activating WhatsApp Business...")
        driver.activate_app("com.whatsapp.w4b")
        print("✅ App activated!")

        driver.quit()
        print("✅ Test complete!")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    simple_test()