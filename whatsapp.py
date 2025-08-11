#!/usr/bin/env python3

from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException
import time
import os
import base64
from datetime import datetime

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

def read_daily_message():
    """Read the daily message from the text file"""
    try:
        with open('daily_message.txt', 'r', encoding='utf-8') as file:
            message = file.read().strip()
            if not message:
                print("daily_message.txt is empty. Please add your message to the file.")
                return None
            return message
    except FileNotFoundError:
        print("daily_message.txt not found. Please create the file with your daily message.")
        return None
    except Exception as e:
        print(f"Error reading daily message: {str(e)}")
        return None

def load_processed_chats_today():
    """Load list of chats that have already been processed today"""
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = f"processed_chats_{today}.txt"
    
    processed_chats = set()
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r', encoding='utf-8') as file:
                for line in file:
                    chat_name = line.strip()
                    if chat_name:
                        processed_chats.add(chat_name)
            print(f"Loaded {len(processed_chats)} previously processed chats from {log_file}")
        except Exception as e:
            print(f"Error loading processed chats: {str(e)}")
    
    return processed_chats, log_file

def save_processed_chat(log_file, chat_name):
    """Save a processed chat to today's log file"""
    try:
        with open(log_file, 'a', encoding='utf-8') as file:
            file.write(f"{chat_name}\n")
    except Exception as e:
        print(f"Error saving processed chat: {str(e)}")

def get_daily_photo_path():
    """Get the path to the only photo in daily_photos folder"""
    photo_extensions = ['.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG']
    
    try:
        if not os.path.exists('daily_photos'):
            return None
            
        # Get all image files in the directory
        image_files = []
        for filename in os.listdir('daily_photos'):
            if any(filename.lower().endswith(ext.lower()) for ext in photo_extensions):
                if not filename.startswith('.') and filename != 'README.md':
                    image_files.append(filename)
        
        if len(image_files) == 1:
            return f'daily_photos/{image_files[0]}'
        elif len(image_files) > 1:
            print(f"Warning: Multiple photos found in daily_photos folder: {image_files}")
            print("Using the first one. Please keep only one photo in the folder.")
            return f'daily_photos/{image_files[0]}'
        else:
            return None
            
    except Exception as e:
        print(f"Error checking daily_photos folder: {str(e)}")
        return None

def transfer_photo_to_device(driver, local_photo_path):
    """Transfer photo from PC to Android device"""
    try:
        # Read the photo file
        with open(local_photo_path, 'rb') as photo_file:
            photo_data = photo_file.read()
        
        # Convert to base64 for transfer
        photo_base64 = base64.b64encode(photo_data).decode('utf-8')
        
        # Push to device Pictures folder
        device_path = '/sdcard/Pictures/whatsapp_daily_poster.jpg'
        driver.push_file(device_path, photo_base64)
        
        print(f"Photo transferred to device: {device_path}")
        return device_path
        
    except Exception as e:
        print(f"Error transferring photo to device: {str(e)}")
        return None

def send_message_with_photo(driver, message):
    """Attach photo first, then add message, then send everything together"""
    try:
        # Step 1: Click attachment button
        attachment_btn = driver.find_element(
            AppiumBy.XPATH,
            "//android.widget.ImageButton[contains(@resource-id, 'attach')]"
        )
        attachment_btn.click()
        time.sleep(2)
        
        # Step 2: Click Gallery option
        gallery_btn = driver.find_element(
            AppiumBy.XPATH,
            "//android.widget.TextView[contains(@text, 'Gallery')]"
        )
        gallery_btn.click()
        time.sleep(3)
        
        # Step 3: Select the first photo in gallery using dynamic XPath
        # This will work regardless of the specific date in the image name
        first_photo = driver.find_element(
            AppiumBy.XPATH,
            "(//android.widget.ImageView[contains(@content-desc, 'Photo, date')])[1]"
        )
        first_photo.click()
        time.sleep(2)
        
        # Step 4: Add message to photo caption
        message_input = driver.find_element(
            AppiumBy.XPATH,
            "//android.widget.EditText[@resource-id='com.whatsapp.w4b:id/caption']"
        )
        message_input.clear()
        message_input.send_keys(message)
        time.sleep(1)
        
        # Step 5: Send the photo with message
        send_photo_btn = driver.find_element(
            AppiumBy.XPATH,
            "//android.widget.ImageButton[contains(@resource-id, 'send')]"
        )
        send_photo_btn.click()
        time.sleep(2)
        
        return True
        
    except Exception as e:
        print(f"Error sending photo with message: {str(e)}")
        return False

def find_next_lucky_taj_chat(driver):
    """Find the first LuckyTaj♠️ chat from top to bottom without unread messages"""
    try:
        # Find all chat titles containing LuckyTaj♠️
        chat_elements = driver.find_elements(
            AppiumBy.XPATH,
            "//android.widget.TextView[contains(@resource-id, 'conversations_row_contact_name') and contains(@text, 'LuckyTaj♠️')]"
        )
        
        # Sort by Y position (top to bottom)
        chat_elements.sort(key=lambda element: element.location['y'])
        
        # Check each chat from top to bottom
        for chat_element in chat_elements:
            try:
                chat_name = chat_element.text
                print(f"Checking chat: {chat_name}")
                
                # Check if this chat has unread messages
                chat_location = chat_element.location
                unread_elements = driver.find_elements(
                    AppiumBy.XPATH,
                    "//android.view.View[contains(@content-desc, 'unread message')]"
                )
                
                has_unread = False
                for unread_elem in unread_elements:
                    unread_location = unread_elem.location
                    if abs(unread_location['y'] - chat_location['y']) <= 50:
                        has_unread = True
                        print(f"Skipping {chat_name} - has unread messages")
                        break
                
                if not has_unread:
                    print(f"Found target chat: {chat_name}")
                    return chat_element
                    
            except Exception as e:
                print(f"Error checking chat: {str(e)}")
                continue
        
        print("No LuckyTaj chats without unread messages found")
        return None
        
    except Exception as e:
        print(f"Error finding LuckyTaj chats: {str(e)}")
        return None

def scroll_down_chat_list(driver):
    """Scroll down in the chat list to find more chats"""
    try:
        screen_size = driver.get_window_size()
        start_x = screen_size['width'] // 2
        start_y = screen_size['height'] * 3 // 4
        end_y = screen_size['height'] // 4
        
        driver.swipe(start_x, start_y, start_x, end_y, 1000)
        time.sleep(1)
        return True
    except Exception as e:
        print(f"Error scrolling: {str(e)}")
        return False

def send_message_to_chat(driver, message):
    """Send message to the currently opened chat"""
    try:
        # Find the message input field
        message_input = driver.find_element(
            AppiumBy.XPATH,
            "//android.widget.EditText[contains(@resource-id, 'entry')]"
        )
        
        # Clear any existing text and send message
        message_input.clear()
        message_input.send_keys(message)
        
        # Find and tap the send button
        send_button = driver.find_element(
            AppiumBy.XPATH,
            "//android.widget.ImageButton[contains(@resource-id, 'send')]"
        )
        send_button.click()
        
        print(f"Message sent: {message}")
        time.sleep(2)
        return True
        
    except Exception as e:
        print(f"Error sending message: {str(e)}")
        return False

def go_back_to_chat_list(driver):
    """Go back to the main chat list from an individual chat"""
    try:
        # Press back button to return to chat list
        driver.press_keycode(4)  # KEYCODE_BACK
        time.sleep(2)
        return True
    except Exception as e:
        print(f"Error going back to chat list: {str(e)}")
        return False

def process_lucky_taj_chats(driver):
    """Main function to find and send messages to all LuckyTaj chats"""
    print("Starting to process LuckyTaj chats...")
    
    # Read the daily message
    daily_message = read_daily_message()
    if daily_message is None:
        print("No message found in daily_message.txt. Stopping automation.")
        return
    
    print(f"Daily message to send: {daily_message}")
    
    # Check and transfer daily photo
    photo_path = get_daily_photo_path()
    device_photo_path = None
    send_photo = False
    
    if photo_path:
        print(f"Found daily photo: {photo_path}")
        device_photo_path = transfer_photo_to_device(driver, photo_path)
        if device_photo_path:
            send_photo = True
            print("Photo will be sent with each message")
        else:
            print("Photo transfer failed. Will send text messages only.")
    else:
        print("No daily photo found in daily_photos/ folder. Will send text messages only.")
        print("To include photos: Place your daily poster as 'daily_poster.jpg' in the daily_photos/ folder")
    
    # Load previously processed chats for today
    processed_chats, log_file = load_processed_chats_today()
    max_scrolls = 15  # Increased scroll limit for better coverage
    scroll_count = 0
    
    while scroll_count < max_scrolls:
        # Find the next LuckyTaj chat from top to bottom
        target_chat = find_next_lucky_taj_chat(driver)
        
        if target_chat:
            try:
                chat_name = target_chat.text
                
                # Skip if already processed
                if chat_name in processed_chats:
                    print(f"Already processed: {chat_name}")
                    scroll_down_chat_list(driver)
                    scroll_count += 1
                    continue
                
                print(f"Processing: {chat_name}")
                
                # Click on the chat
                target_chat.click()
                time.sleep(2)
                
                # Send the daily message (with photo if available)
                if send_photo:
                    success = send_message_with_photo(driver, daily_message)
                else:
                    success = send_message_to_chat(driver, daily_message)
                
                if success:
                    message_type = "message + photo" if send_photo else "message"
                    print(f"✓ Successfully sent {message_type} to: {chat_name}")
                    processed_chats.add(chat_name)
                    save_processed_chat(log_file, chat_name)
                else:
                    message_type = "message + photo" if send_photo else "message"
                    print(f"✗ Failed to send {message_type} to: {chat_name}")
                    processed_chats.add(chat_name)
                    save_processed_chat(log_file, f"FAILED: {chat_name}")
                
                # Go back to chat list
                go_back_to_chat_list(driver)
                
                # Continue to find more chats
                continue
                
            except Exception as e:
                print(f"Error processing chat: {str(e)}")
                go_back_to_chat_list(driver)
                continue
        
        else:
            # No more LuckyTaj chats found, scroll down
            print(f"No more LuckyTaj chats on screen. Scrolling... ({scroll_count + 1}/{max_scrolls})")
            if scroll_down_chat_list(driver):
                scroll_count += 1
                time.sleep(2)
            else:
                print("Cannot scroll further, ending search")
                break
    
    print(f"Processing complete! Sent messages to {len(processed_chats)} LuckyTaj chats:")
    for chat_name in processed_chats:
        print(f"  - {chat_name}")

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
                time.sleep(3)
                
                # Process LuckyTaj chats and send daily messages
                process_lucky_taj_chats(driver)
                
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