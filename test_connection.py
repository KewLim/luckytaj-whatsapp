#!/usr/bin/env python3

from appium.webdriver.webdriver import WebDriver
from appium.options.android.uiautomator2.base import UiAutomator2Options
import time

def test_connection():
    """Test basic Appium connection"""
    print("Testing Appium connection...")

    try:
        # Set up options
        options = UiAutomator2Options()
        options.platform_name = "Android"
        options.device_name = "Android Device"
        options.automation_name = "UiAutomator2"
        options.app_package = "com.whatsapp"
        options.app_activity = "com.whatsapp.HomeActivity"
        options.no_reset = True
        options.full_reset = False

        # Add timeout options
        options.new_command_timeout = 60  # 1 minute timeout
        options.uiautomator2_server_launch_timeout = 30000  # 30 seconds
        options.uiautomator2_server_install_timeout = 30000  # 30 seconds

        print("Connecting to Appium server...")
        # Connect with shorter timeout for testing
        driver = WebDriver("http://localhost:4723", options=options)

        print("✅ Successfully connected to device!")

        # Test basic command
        print("Testing basic command...")
        window_size = driver.get_window_size()
        print(f"✅ Screen size: {window_size['width']}x{window_size['height']}")

        # Test app activation
        print("Testing app activation...")
        driver.activate_app("com.whatsapp")
        print("✅ App activated successfully!")

        time.sleep(2)

        driver.quit()
        print("✅ Test completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_connection()