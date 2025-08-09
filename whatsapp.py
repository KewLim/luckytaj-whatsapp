#!/usr/bin/env python3

from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
import time

def setup_driver():
    """Initialize Appium driver with Android capabilities"""
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.device_name = "Android Device"
    options.automation_name = "UiAutomator2"
    options.no_reset = True
    options.full_reset = False
    
    # Connect to Appium server
    driver = webdriver.Remote("http://localhost:4723", options=options)
    return driver


def turn_screen_on_and_unlock(driver):
    """Turn on screen and unlock the device"""
    try:
        print("Checking device screen state...")
        
        # First, ensure screen is awake using wake key
        driver.press_keycode(224)  # KEYCODE_WAKEUP (safer than power toggle)
        time.sleep(1)
        
        # Verify screen is responsive
        screen_size = driver.get_window_size()
        print(f"Screen active - size: {screen_size['width']}x{screen_size['height']}")
        
        # Attempt to unlock with swipe up gesture
        print("Attempting to unlock device...")
        
        start_x = screen_size['width'] // 2
        start_y = screen_size['height'] - 200
        end_y = screen_size['height'] // 3
        
        # Swipe up to unlock
        driver.swipe(start_x, start_y, start_x, end_y, 800)
        time.sleep(1)
        
        # Single wake signal and minimal user activity to prevent sleep
        driver.press_keycode(224)  # KEYCODE_WAKEUP
        driver.tap([(50, 50)])  # Single tap to simulate user presence
        
        print("Device unlocked and kept awake")
        return True
            
    except Exception as e:
        print(f"Error during unlock process: {str(e)}")
        return False

def go_to_home_screen(driver):
    """Go to home screen using home keycode - faster than tapping"""
    try:
        print("Going to home screen...")
        
        # Use home keycode - much faster than calculating tap coordinates
        driver.press_keycode(3)  # KEYCODE_HOME
        time.sleep(0.5)  # Reduced sleep time
        
        print("Home screen accessed!")
        return True
        
    except Exception as e:
        print(f"Error going to home screen: {str(e)}")
        return False

def open_whatsapp(driver):
    """Open WhatsApp application"""
    try:
        print("Opening WhatsApp...")
        
        # Method 1: Try to start WhatsApp activity directly
        driver.start_activity("com.whatsapp", "com.whatsapp.HomeActivity")
        time.sleep(3)
        
        print("WhatsApp opened successfully!")
        return True
        
    except Exception as e:
        print(f"Failed to open WhatsApp directly, trying alternative method: {str(e)}")
        
        try:
            # Method 2: Use app package to launch
            driver.activate_app("com.whatsapp")
            time.sleep(3)
            print("WhatsApp opened using activate_app!")
            return True
            
        except Exception as e2:
            print(f"Failed to open WhatsApp with activate_app: {str(e2)}")
            
            try:
                # Method 3: Find and tap WhatsApp icon on home screen
                print("Trying to find WhatsApp on home screen...")
                
                # Go to home screen first
                driver.press_keycode(3)  # KEYCODE_HOME
                time.sleep(2)
                
                # Try to find WhatsApp by text
                whatsapp_element = driver.find_element(AppiumBy.XPATH, "//android.widget.TextView[@text='WhatsApp']")
                whatsapp_element.click()
                time.sleep(3)
                
                print("WhatsApp opened by clicking icon!")
                return True
                
            except Exception as e3:
                print(f"Failed to find WhatsApp icon: {str(e3)}")
                
                try:
                    # Method 4: Open app drawer and search
                    print("Trying app drawer method...")
                    
                    # Swipe up from bottom to open app drawer
                    screen_size = driver.get_window_size()
                    start_x = screen_size['width'] // 2
                    start_y = screen_size['height'] - 100
                    end_y = screen_size['height'] // 2
                    
                    driver.swipe(start_x, start_y, start_x, end_y, 1000)
                    time.sleep(2)
                    
                    # Try to find WhatsApp in app drawer
                    whatsapp_element = driver.find_element(AppiumBy.XPATH, "//android.widget.TextView[@text='WhatsApp']")
                    whatsapp_element.click()
                    time.sleep(3)
                    
                    print("WhatsApp opened from app drawer!")
                    return True
                    
                except Exception as e4:
                    print(f"All methods failed to open WhatsApp: {str(e4)}")
                    print("Please ensure WhatsApp is installed on the device")
                    return False

def open_whatsapp_business(driver):
    """Open WhatsApp Business application - optimized for speed"""
    try:
        print("Opening WhatsApp Business...")
        
        # Method 1: Use activate_app first (most reliable and fastest)
        driver.activate_app("com.whatsapp.w4b")
        time.sleep(1.5)  # Reduced wait time
        print("WhatsApp Business opened using activate_app!")
        return True
            
    except Exception as e:
        print(f"Failed to open WhatsApp Business with activate_app: {str(e)}")
        
        try:
            # Method 2: Try start_activity as fallback
            driver.start_activity("com.whatsapp.w4b", "com.whatsapp.HomeActivity")
            time.sleep(1.5)
            
            print("WhatsApp Business opened using start_activity!")
            return True
            
        except Exception as e2:
            print(f"Failed to open WhatsApp Business with start_activity: {str(e2)}")
            
            try:
                # Method 3: Find and tap WhatsApp Business icon (faster search)
                print("Searching for WhatsApp Business icon...")
                
                # Try multiple possible text variations
                possible_texts = ["WhatsApp Business", "WA Business", "WhatsApp Biz"]
                
                for text in possible_texts:
                    try:
                        whatsapp_element = driver.find_element(AppiumBy.XPATH, f"//android.widget.TextView[@text='{text}']")
                        whatsapp_element.click()
                        time.sleep(1.5)
                        print(f"WhatsApp Business opened by clicking '{text}' icon!")
                        return True
                    except:
                        continue
                
                print("WhatsApp Business icon not found on current screen")
                return False
                
            except Exception as e3:
                print(f"All methods failed to open WhatsApp Business: {str(e3)}")
                print("Please ensure WhatsApp Business is installed on the device")
                return False

def main():
    """Main function to control screen and unlock"""
    driver = None
    
    try:
        print("Starting Appium session...")
        driver = setup_driver()
        
        print("Attempting to turn on screen and unlock device...")
        success = turn_screen_on_and_unlock(driver)
        
        if success:
            print("Device is ready for automation!")


            # Swipe to home screen to ensure we're on home screen
            
            # Open WhatsApp Business after successful unlock
            whatsapp_success = open_whatsapp_business(driver)
            
            if whatsapp_success:
                print("WhatsApp Business is now open and ready for use!")
                # Brief pause to ensure app is fully loaded
                time.sleep(2)
            else:
                print("Failed to open WhatsApp Business, but device is unlocked")
            
        else:
            print("Unable to fully unlock device")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        print("Make sure:")
        print("1. Appium server is running (appium)")
        print("2. Android device is connected via USB")
        print("3. USB debugging is enabled")
        print("4. Device is detected (adb devices)")
        
    finally:
        if driver:
            print("Closing Appium session...")
            driver.quit()

if __name__ == "__main__":
    main()