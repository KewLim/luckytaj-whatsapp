#!/usr/bin/env python3

from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import base64
import signal
import sys
from datetime import datetime

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\033[1;35m\n\n🛑 Stopping automation (Ctrl+C pressed)...\033[0m")
    print("Cleaning up...")
    try:
        # Try to quit driver if it exists
        import gc
        for obj in gc.get_objects():
            if hasattr(obj, 'quit') and 'webdriver' in str(type(obj)):
                obj.quit()
                break
    except:
        pass
    os._exit(0)

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
    """Optimized photo + message sending - target: under 8 seconds"""
    start_time = time.time()
    print(f"[INFO] Fast photo + message send...")
    
    try:
        wait = WebDriverWait(driver, timeout=10, poll_frequency=0.2)  #  second timeout for each element
        
        # Step 1: Click attachment button (parallel search with EC.any_of)
        step_start = time.time()
        attachment_selectors = [
            (AppiumBy.ID, "com.whatsapp.w4b:id/attach"),
            (AppiumBy.XPATH, "//*[@resource-id='com.whatsapp.w4b:id/attach']"),
            (AppiumBy.XPATH, "//android.widget.ImageButton[contains(@resource-id, 'attach')]")
        ]
        
        # Use EC.any_of for parallel search
        attachment_btn = wait.until(
            EC.any_of(
                *[EC.element_to_be_clickable(selector) for selector in attachment_selectors]
            )
        )
        attachment_btn.click()
        time.sleep(0.8)  # Reduced from 2s
        print(f"[INFO] Attachment clicked ({time.time() - step_start:.2f}s)")
        
        # Step 2: Click Gallery 
        step_start = time.time()
        gallery_selectors = [
            (AppiumBy.XPATH, "//*[@text='Gallery']"),
            (AppiumBy.XPATH, "//android.widget.TextView[@text='Gallery']")
        ]
        
        gallery_btn = None
        for selector_type, selector in gallery_selectors:
            try:
                gallery_btn = wait.until(EC.element_to_be_clickable((selector_type, selector)))
                break
            except TimeoutException:
                continue
                
        if not gallery_btn:
            raise Exception("Gallery button not found")
            
        gallery_btn.click()
        time.sleep(1.2)  # Reduced from 3s
        print(f"🖼️ Gallery opened ({time.time() - step_start:.2f}s)")
        
        # Step 3: Select first photo (fast optimized selectors)
        step_start = time.time()
        fast_wait = WebDriverWait(driver, timeout=3, poll_frequency=0.1)  # Much faster timeout
        
        photo_selectors = [
            # More specific and faster selectors
            (AppiumBy.XPATH, "//android.widget.ImageView[1]"),
            (AppiumBy.XPATH, "(//android.widget.ImageView)[1]"),
            (AppiumBy.XPATH, "//*[contains(@content-desc, 'Photo')][1]"),
            (AppiumBy.XPATH, "(//android.widget.ImageView[contains(@content-desc, 'Photo')])[1]"),
            (AppiumBy.CLASS_NAME, "android.widget.ImageView"),  # Fallback to first ImageView
            (AppiumBy.XPATH, "//*[@clickable='true'][1]")  # Last resort - first clickable element
        ]
        
        first_photo = WebDriverWait(driver, timeout=5, poll_frequency=0.1).until(
            EC.any_of(*[EC.element_to_be_clickable(sel) for sel in photo_selectors])
        )
        first_photo.click()
        print(f"📸 Photo selected ({time.time() - step_start:.2f}s)")
        
        # Step 4: Add caption (parallel search with EC.any_of)
        step_start = time.time()
        caption_selectors = [
            (AppiumBy.ID, "com.whatsapp.w4b:id/caption"),
            (AppiumBy.XPATH, "//*[@resource-id='com.whatsapp.w4b:id/caption']"),
            (AppiumBy.XPATH, "//android.widget.EditText[contains(@resource-id, 'caption')]")
        ]
        
        # Use EC.any_of for parallel search
        message_input = wait.until(
            EC.any_of(
                *[EC.element_to_be_clickable(selector) for selector in caption_selectors]
            )
        )
        
        # Fast text input using direct method
        message_input.click()
        time.sleep(0.1)
        message_input.clear()
        
        # Use fast text input - try multiple methods
        try:
            # Method 1: Direct value setting (fastest)
            driver.execute_script("mobile: type", {"text": message})
        except:
            try:
                # Method 2: ADB input (fast)
                message_input.send_keys(message)
            except:
                # Method 3: Fallback
                for char in message:
                    message_input.send_keys(char)
                    
        print(f"✏️ Caption added ({time.time() - step_start:.2f}s)")
        
        # Step 5: Send (parallel search with EC.any_of)
        step_start = time.time()
        send_selectors = [
            (AppiumBy.ID, "com.whatsapp.w4b:id/send"),
            (AppiumBy.XPATH, "//*[@resource-id='com.whatsapp.w4b:id/send']"),
            (AppiumBy.XPATH, "//android.widget.ImageButton[contains(@resource-id, 'send')]")
        ]
        
        # Use EC.any_of for parallel search
        send_btn = wait.until(
            EC.any_of(
                *[EC.element_to_be_clickable(selector) for selector in send_selectors]
            )
        )
        
        send_btn.click()
        time.sleep(0.8)  # Reduced from 2s
        print(f"📤 Sent ({time.time() - step_start:.2f}s)")
        
        total_time = time.time() - start_time
        print(f"🎉 Photo+message sent! Total: {total_time:.2f}s")
        return True
        
    except Exception as e:
        total_time = time.time() - start_time
        print(f"❌ Error after {total_time:.2f}s: {str(e)}")
        return False

def find_next_lucky_taj_chat(driver):
    """Find the first LuckyTaj♠️ chat by checking numbered xpath positions with parallel search"""
    search_start = time.time()
    print(f"[INFO] Searching for LuckyTaj chats using numbered xpath...")
    
    try:
        wait = WebDriverWait(driver, timeout=5, poll_frequency=0.2)
        
        # Start checking from chat position [1] and increment
        chat_position = 1
        max_chats_to_check = 50  # Reasonable limit to avoid infinite loop
        
        while chat_position <= max_chats_to_check:
            try:
                print(f"[Search] Checking chat position [{chat_position}]...")
                
                # Use numbered xpath with parallel search for better reliability
                chat_container_selectors = [
                    (AppiumBy.XPATH, f"(//android.widget.LinearLayout[@resource-id='com.whatsapp.w4b:id/contact_row_container'])[{chat_position}]"),
                    (AppiumBy.XPATH, f"(//android.widget.LinearLayout[contains(@resource-id, 'contact_row_container')])[{chat_position}]"),
                    (AppiumBy.XPATH, f"(//android.view.ViewGroup[@resource-id='com.whatsapp.w4b:id/contact_row_container'])[{chat_position}]")
                ]
                
                # Use EC.any_of for parallel search of chat container
                try:
                    chat_container = wait.until(
                        EC.any_of(
                            *[EC.presence_of_element_located(selector) for selector in chat_container_selectors]
                        )
                    )
                except TimeoutException:
                    print(f"❌ No more chats found at position [{chat_position}]")
                    break
                
                # Get chat name from this container using parallel search
                chat_name_selectors = [
                    (AppiumBy.XPATH, ".//android.widget.TextView[contains(@resource-id, 'conversations_row_contact_name')]"),
                    (AppiumBy.XPATH, ".//android.widget.TextView[contains(@resource-id, 'contact_name')]"),
                    (AppiumBy.XPATH, ".//android.widget.TextView[@content-desc]")
                ]
                
                chat_name_element = None
                for selector_type, selector in chat_name_selectors:
                    try:
                        chat_name_element = chat_container.find_element(selector_type, selector)
                        break
                    except:
                        continue
                
                if not chat_name_element:
                    print(f"⏭️ Skipping position [{chat_position}] - no chat name found")
                    chat_position += 1
                    continue
                
                chat_name = chat_name_element.text
                print(f"[Found] Chat at position [{chat_position}]: {chat_name}")
                
                # Check if this chat contains "LuckyTaj♠️"
                if "LuckyTaj♠️" in chat_name:
                    # Check if this chat has unread messages
                    unread_check_start = time.time()
                    try:
                        unread_element = chat_container.find_element(
                            AppiumBy.XPATH, 
                            ".//android.view.View[contains(@content-desc, 'unread message')]"
                        )
                        unread_check_time = time.time() - unread_check_start
                        print(f"⏭️ Skipping {chat_name} - has unread messages (check took {unread_check_time:.2f}s)")
                        chat_position += 1
                        continue
                    except:
                        # No unread messages found, this is our target
                        total_time = time.time() - search_start
                        print(f"\033[1;35m🎯 Found target chat: {chat_name} at position [{chat_position}] (total search time: {total_time:.2f}s)\033[0m")
                        return chat_container
                
                # Not a LuckyTaj chat, continue to next position
                chat_position += 1
                
            except Exception as e:
                print(f"❌ Error checking position [{chat_position}]: {str(e)}")
                chat_position += 1
                continue
        
        total_time = time.time() - search_start
        print(f"❌ No LuckyTaj chats without unread messages found after checking {chat_position-1} positions (total time: {total_time:.2f}s)")
        return None
        
    except Exception as e:
        total_time = time.time() - search_start
        print(f"❌ Error finding LuckyTaj chats after {total_time:.2f}s: {str(e)}")
        return None

def scroll_down_chat_list(driver):
    """Scroll down in the chat list to find more chats"""
    try:
        scroll_start = time.time()
        print(f"📜 Scrolling down chat list...")
        
        screen_size = driver.get_window_size()
        start_x = screen_size['width'] // 2
        start_y = screen_size['height'] * 3 // 4
        end_y = screen_size['height'] // 4
        
        driver.swipe(start_x, start_y, start_x, end_y, 400)  # Faster swipe
        time.sleep(0.5)  # Reduced wait time
        
        scroll_time = time.time() - scroll_start
        print(f"✓ Scroll completed in {scroll_time:.2f}s")
        return True
    except Exception as e:
        scroll_time = time.time() - scroll_start
        print(f"❌ Error scrolling after {scroll_time:.2f}s: {str(e)}")
        return False

def send_message_to_chat(driver, message):
    """Optimized text message sending - target: under 3 seconds"""
    start_time = time.time()
    print(f"[INFO] Fast text send...")
    
    try:
        wait = WebDriverWait(driver, 2)  # 2 second timeout
        
        # Find message input (faster selectors)
        input_selectors = [
            (AppiumBy.ID, "com.whatsapp.w4b:id/entry"),
            (AppiumBy.XPATH, "//*[@resource-id='com.whatsapp.w4b:id/entry']"),
            (AppiumBy.XPATH, "//android.widget.EditText[contains(@resource-id, 'entry')]")
        ]
        
        message_input = None
        for selector_type, selector in input_selectors:
            try:
                message_input = wait.until(EC.element_to_be_clickable((selector_type, selector)))
                break
            except TimeoutException:
                continue
                
        if not message_input:
            raise Exception("Message input not found")
        
        # Fast text input
        step_start = time.time()
        message_input.click()
        message_input.clear()
        
        # Try fast text input methods
        try:
            driver.execute_script("mobile: type", {"text": message})
        except:
            message_input.send_keys(message)
            
        print(f"📝 Text entered ({time.time() - step_start:.2f}s)")
        
        # Find and click send button (faster)
        send_selectors = [
            (AppiumBy.ID, "com.whatsapp.w4b:id/send"),
            (AppiumBy.XPATH, "//*[@resource-id='com.whatsapp.w4b:id/send']"),
            (AppiumBy.XPATH, "//android.widget.ImageButton[contains(@resource-id, 'send')]")
        ]
        
        send_button = None
        for selector_type, selector in send_selectors:
            try:
                send_button = wait.until(EC.element_to_be_clickable((selector_type, selector)))
                break
            except TimeoutException:
                continue
                
        if not send_button:
            raise Exception("Send button not found")
            
        send_button.click()
        time.sleep(0.5)  # Reduced from 2s
        
        total_time = time.time() - start_time
        print(f"🎉 Text sent! Total: {total_time:.2f}s")
        return True
        
    except Exception as e:
        total_time = time.time() - start_time
        print(f"❌ Error after {total_time:.2f}s: {str(e)}")
        return False

def go_back_to_chat_list(driver):
    """Go back to the main chat list from an individual chat"""
    try:
        # Press back button to return to chat list
        driver.press_keycode(4)  # KEYCODE_BACK
        time.sleep(1.5)
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
    max_scrolls = 100  # Increased scroll limit for better coverage
    scroll_count = 0
    
    overall_start = time.time()
    print(f"[INFO] Starting chat processing loop (max {max_scrolls} scrolls)")
    
    while scroll_count < max_scrolls:
        # Find the next LuckyTaj chat from top to bottom
        print(f"\n[INFO] Loop iteration {scroll_count + 1}/{max_scrolls}")
        target_chat = find_next_lucky_taj_chat(driver)
        
        if target_chat:
            try:
                chat_processing_start = time.time()
                chat_name = target_chat.text
                
                # Skip if already processed
                if chat_name in processed_chats:
                    print(f"⏭️ Already processed: {chat_name}")
                    scroll_down_chat_list(driver)
                    scroll_count += 1
                    continue
                
                print(f"\033[1;33m🔄 Processing: {chat_name}\033[0m")
                
                # Click on the chat
                click_start = time.time()
                print(f"[INFO] Clicking on chat: {chat_name}")
                target_chat.click()
                time.sleep(1)  # Reduced from 2s
                click_time = time.time() - click_start
                print(f"[CHECKED] Chat opened in {click_time:.2f}s")
                
                # Send the daily message (with photo if available)
                message_start = time.time()
                if send_photo:
                    success = send_message_with_photo(driver, daily_message)
                else:
                    success = send_message_to_chat(driver, daily_message)
                message_time = time.time() - message_start
                
                if success:
                    message_type = "message + photo" if send_photo else "message"
                    print(f"✅ Successfully sent {message_type} to: {chat_name} (message time: {message_time:.2f}s)")
                    processed_chats.add(chat_name)
                    save_processed_chat(log_file, chat_name)
                else:
                    message_type = "message + photo" if send_photo else "message"
                    print(f"❌ Failed to send {message_type} to: {chat_name} (failed after: {message_time:.2f}s)")
                    processed_chats.add(chat_name)
                    save_processed_chat(log_file, f"FAILED: {chat_name}")
                
                # Go back to chat list
                back_start = time.time()
                print(f"🔙 Going back to chat list...")
                driver.press_keycode(4)  # KEYCODE_BACK - faster than function call
                time.sleep(0.8)  # Reduced from 2s
                back_time = time.time() - back_start
                print(f"[CHECKED] Returned to chat list in {back_time:.2f}s")
                
                total_chat_time = time.time() - chat_processing_start
                print(f"⏱️ Total time for {chat_name}: {total_chat_time:.2f}s")
                print(f"   - Chat click + open: {click_time:.2f}s")
                print(f"   - Message sending: {message_time:.2f}s") 
                print(f"   - Back to list: {back_time:.2f}s")
                print("─" * 50)
                
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
                time.sleep(0.5)  # Reduced from 2s
            else:
                print("Cannot scroll further, ending search")
                break
    
    overall_time = time.time() - overall_start
    print(f"\n[INFO] Processing complete! Total time: {overall_time:.2f}s")
    print(f"[INFO] Summary:")
    print(f"   - Chats processed: {len(processed_chats)}")
    print(f"   - Scrolls performed: {scroll_count}/{max_scrolls}")
    print(f"   - Average time per chat: {overall_time/max(len(processed_chats), 1):.2f}s")
    print(f"\n[INFO] Sent messages to {len(processed_chats)} LuckyTaj chats:")
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
            
            # Open WhatsApp Business after successful unlock
            whatsapp_success = open_whatsapp_business(driver)
            
            if whatsapp_success:
                print("WhatsApp Business is now open and ready for use!")
                # Brief pause to ensure app is fully loaded
                time.sleep(1.8)
                
                # Scroll up to ensure filter buttons are visible
                try:
                    print("Scrolling up to reveal filter buttons...")
                    driver.swipe(540, 300, 540, 600, 200)  # Swipe from middle-top to middle-bottom
                    time.sleep(0.1)
                    print("Scroll up completed")
                except Exception as e:
                    print(f"Failed to scroll up: {str(e)}")
                
                # Click on Groups filter button first
                try:
                    print("Looking for Groups filter button...")
                    group_button = driver.find_element(AppiumBy.XPATH, "//android.widget.RadioButton[contains(@content-desc, 'Groups filter') and contains(@content-desc, 'unselected')]")
                    print("Found Groups filter button, clicking...")
                    group_button.click()
                    time.sleep(1)
                    print("Successfully clicked Groups filter")
                except Exception as e:
                    print(f"Groups filter button not found or already selected: {str(e)}")
                
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
    # Set up signal handlers for stopping
    signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Kill command
    print("🚦 Press Ctrl+C to stop the automation at any time")
    print("   (Note: On macOS terminal, use Ctrl+C, not Cmd+C)")
    main()