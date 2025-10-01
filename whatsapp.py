#!/usr/bin/env python3

from appium.webdriver.webdriver import WebDriver
from appium.options.android.uiautomator2.base import UiAutomator2Options
from selenium.webdriver.common.by import By as AppiumBy
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import base64
import signal
from datetime import datetime, timezone, timedelta

# GMT+7 timezone
GMT_PLUS_7 = timezone(timedelta(hours=7))

# Configuration: Chat name prefix to remove before searching
CHAT_NAME_PREFIX_TO_REMOVE = "NepalWin🇳🇵"  # Change this to customize what prefix to remove

def clean_chat_name(chat_name):
    """Remove configured prefix from chat name for searching and handle various formats"""
    # Handle names that already have the prefix removed or never had it
    if CHAT_NAME_PREFIX_TO_REMOVE and chat_name.startswith(CHAT_NAME_PREFIX_TO_REMOVE):
        cleaned_name = chat_name.replace(CHAT_NAME_PREFIX_TO_REMOVE, "", 1).strip()
        print(f"[CLEAN] Cleaned '{chat_name}' -> '{cleaned_name}'")
        return cleaned_name
    else:
        # For names that don't have the prefix (like "Shankartr88"), use them as-is
        print(f"[CLEAN] Using name as-is: '{chat_name}'")
        return chat_name.strip()

def get_gmt7_time():
    """Get current time in GMT+7 timezone"""
    return datetime.now(GMT_PLUS_7)

def format_gmt7_time(dt=None):
    """Format datetime as string in GMT+7"""
    if dt is None:
        dt = get_gmt7_time()
    return dt.strftime("%Y-%m-%d %H:%M:%S GMT+7")

# Global variable to track if timestamp was written for this session
_timestamp_written_today = False

def log_not_found_chat(chat_name, row_number=None):
    """Log chat name that was not found to a file with timestamp"""
    global _timestamp_written_today

    try:
        log_filename = f"txt/not_found_chats_{get_gmt7_time().strftime('%Y%m%d')}.txt"

        # Create txt directory if it doesn't exist
        os.makedirs('txt', exist_ok=True)

        with open(log_filename, 'a', encoding='utf-8') as file:
            # Write timestamp only once per script run
            if not _timestamp_written_today:
                timestamp = format_gmt7_time()
                file.write(f"[{timestamp}]\n")
                _timestamp_written_today = True

            file.write(f"{chat_name}\n")

        print(f"[LOG] Recorded not found chat: {chat_name} in {log_filename}")

    except Exception as e:
        print(f"[ERROR] Failed to log not found chat: {str(e)}")


def log_script_event(event_type, message=""):
    """Log script start/end events with GMT+7 timestamp"""
    try:
        log_filename = f"txt/script_log_{get_gmt7_time().strftime('%Y%m%d')}.txt"

        # Create txt directory if it doesn't exist
        os.makedirs('txt', exist_ok=True)

        timestamp = format_gmt7_time()
        log_entry = f"[{timestamp}] {event_type.upper()}: {message}\n"

        with open(log_filename, 'a', encoding='utf-8') as file:
            file.write(log_entry)

        print(f"[LOG] {event_type.upper()}: {message}")

    except Exception as e:
        print(f"[ERROR] Failed to log script event: {str(e)}")

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
    options.app_package = "com.whatsapp"
    options.app_activity = "com.whatsapp.home.ui.HomeActivity"
    options.no_reset = True
    options.full_reset = False

    # Add session stability options
    options.new_command_timeout = 300  # 5 minutes timeout
    options.uiautomator2_server_launch_timeout = 60000  # 60 seconds
    options.uiautomator2_server_install_timeout = 60000  # 60 seconds

    # Connect to Appium server
    driver = WebDriver("http://localhost:4723", options=options)
    return driver

def is_driver_alive(driver):
    """Check if the driver session is still alive"""
    try:
        driver.get_window_size()  # Simple command to test session
        return True
    except Exception:
        return False

def recover_session(driver, max_attempts=3):
    """Attempt to recover the Appium session with multiple strategies"""
    for attempt in range(max_attempts):
        try:
            print(f"[RECOVERY] Attempting to recover Appium session... (Attempt {attempt + 1}/{max_attempts})")

            # Strategy 1: Try to gracefully quit the old session
            if driver:
                try:
                    print("[RECOVERY] Attempting graceful session cleanup...")
                    driver.quit()
                    print("[RECOVERY] Old session cleaned up")
                except Exception as quit_error:
                    print(f"[RECOVERY] Session cleanup failed: {quit_error}")

            # Strategy 2: Wait a bit for resources to be released
            time.sleep(2 + attempt)  # Progressive delay

            # Strategy 3: Create new session with enhanced error handling
            try:
                print("[RECOVERY] Creating new Appium session...")
                new_driver = setup_driver()
                print("[RECOVERY] New session created successfully")
            except Exception as setup_error:
                print(f"[RECOVERY] Failed to create new session: {setup_error}")
                if attempt < max_attempts - 1:
                    print(f"[RECOVERY] Retrying in {3 + attempt} seconds...")
                    time.sleep(3 + attempt)
                    continue
                else:
                    return None

            # Strategy 4: Re-initialize device and WhatsApp
            print("[RECOVERY] Re-initializing device and WhatsApp...")

            # Turn on screen and unlock
            unlock_success = turn_screen_on_and_unlock(new_driver)
            if not unlock_success:
                print("[RECOVERY] Failed to unlock device")
                if attempt < max_attempts - 1:
                    try:
                        new_driver.quit()
                    except:
                        pass
                    continue
                else:
                    return None

            # Brief pause for device to stabilize
            adaptive_wait(new_driver, 1.5, 3.0)

            # Open WhatsApp with improved detection
            whatsapp_success = open_whatsapp_business(new_driver)
            if whatsapp_success:
                print("[RECOVERY] Session recovered successfully!")
                return new_driver
            else:
                print("[RECOVERY] Failed to re-open WhatsApp")
                if attempt < max_attempts - 1:
                    try:
                        new_driver.quit()
                    except:
                        pass
                    continue
                else:
                    return None

        except Exception as e:
            print(f"[RECOVERY] Recovery attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_attempts - 1:
                print(f"[RECOVERY] Retrying recovery in {3 + attempt} seconds...")
                time.sleep(3 + attempt)
            else:
                print("[RECOVERY] All recovery attempts failed")
                return None

    return None

def safe_operation(operation, *args, retry_count=2, **kwargs):
    """Wrapper for safe execution of operations with auto-retry and recovery"""
    for attempt in range(retry_count + 1):
        try:
            return operation(*args, **kwargs)
        except Exception as e:
            print(f"[SAFE_OP] Operation '{operation.__name__}' failed (attempt {attempt + 1}): {e}")

            # Check if it's a driver-related error that needs recovery
            driver_errors = ["session", "connection", "socket", "timeout", "network"]
            if any(error_term in str(e).lower() for error_term in driver_errors):
                print(f"[SAFE_OP] Detected driver-related error, may need session recovery")

            if attempt < retry_count:
                print(f"[SAFE_OP] Retrying operation in {1 + attempt} seconds...")
                time.sleep(1 + attempt)
            else:
                print(f"[SAFE_OP] Operation '{operation.__name__}' failed after {retry_count + 1} attempts")
                raise e


def turn_screen_on_and_unlock(driver):
    """Turn on screen and unlock the device"""
    try:
        print("Checking device screen state...")
        
        # First, ensure screen is awake using wake key
        driver.press_keycode(224)  # KEYCODE_WAKEUP (safer than power toggle)
        time.sleep(.5)
        
        # Verify screen is responsive
        screen_size = driver.get_window_size()
        print(f"Screen active - size: {screen_size['width']}x{screen_size['height']}")
        
        # Single wake signal and minimal user activity to prevent sleep
        driver.press_keycode(224)  # KEYCODE_WAKEUP
        driver.tap([(50, 50)])  # Single tap to simulate user presence
        
        print("Device unlocked and kept awake")
        return True
            
    except Exception as e:
        print(f"Error during unlock process: {str(e)}")
        return False



def wait_for_whatsapp_loaded(driver, timeout=15):
    """Wait for WhatsApp to be fully loaded with proper backend checks"""
    print("[LOAD] Waiting for WhatsApp to fully load...")
    wait = WebDriverWait(driver, timeout)

    try:
        # Wait for main WhatsApp elements to be present and stable
        main_indicators = [
            # Main chat list indicators
            (AppiumBy.XPATH, "//*[@text='WhatsApp']"),
            (AppiumBy.XPATH, "//*[@text='Chats']"),
            (AppiumBy.ID, "com.whatsapp:id/menuitem_search"),
            (AppiumBy.ID, "com.whatsapp:id/search"),
            # Floating action button (new chat)
            (AppiumBy.ID, "com.whatsapp:id/fab"),
        ]

        # Wait for at least one main indicator to be present
        element_found = False
        for selector_type, selector in main_indicators:
            try:
                element = wait.until(EC.presence_of_element_located((selector_type, selector)))
                if element.is_displayed():
                    print(f"[LOAD] Found main element: {selector}")
                    element_found = True
                    break
            except TimeoutException:
                continue

        if not element_found:
            print("[LOAD] No main WhatsApp elements found")
            return False

        # Additional stability check - wait a bit more for backend to settle
        print("[LOAD] Main elements found, waiting for backend stability...")
        time.sleep(2.5)  # Allow backend processes to complete

        # Verify app is still responsive
        try:
            driver.get_window_size()  # Simple responsiveness test
            print("[LOAD] WhatsApp is fully loaded and responsive")
            return True
        except:
            print("[LOAD] App became unresponsive")
            return False

    except Exception as e:
        print(f"[LOAD] Error waiting for WhatsApp: {e}")
        return False

def open_whatsapp_business(driver):
    """Open WhatsApp application with improved reliability and loading detection"""
    max_attempts = 3

    for attempt in range(max_attempts):
        print(f"Opening WhatsApp... (Attempt {attempt + 1}/{max_attempts})")

        try:
            # Method 1: Use activate_app first (most reliable)
            print("[OPEN] Trying activate_app method...")
            driver.activate_app("com.whatsapp")
            time.sleep(1)  # Brief wait for app launch

            # Check if app actually opened
            if wait_for_whatsapp_loaded(driver):
                print("[SUCCESS] WhatsApp opened using activate_app!")
                return True
            else:
                print("[FAIL] activate_app launched but app not properly loaded")

        except Exception as e:
            print(f"[FAIL] activate_app failed: {str(e)}")

        try:
            # Method 2: Try start_activity as fallback
            print("[OPEN] Trying start_activity method...")
            driver.start_activity("com.whatsapp", "com.whatsapp.home.ui.HomeActivity")
            time.sleep(1.5)

            if wait_for_whatsapp_loaded(driver):
                print("[SUCCESS] WhatsApp opened using start_activity!")
                return True
            else:
                print("[FAIL] start_activity launched but app not properly loaded")

        except Exception as e2:
            print(f"[FAIL] start_activity failed: {str(e2)}")

        try:
            # Method 3: Find and tap WhatsApp icon with better detection
            print("[OPEN] Trying icon tap method...")

            # Enhanced icon search with more selectors
            icon_selectors = [
                (AppiumBy.XPATH, "//android.widget.TextView[@text='WhatsApp']"),
                (AppiumBy.XPATH, "//android.widget.TextView[@text='WA']"),
                (AppiumBy.XPATH, "//*[contains(@text, 'WhatsApp')]"),
                (AppiumBy.XPATH, "//*[@content-desc='WhatsApp']"),
                (AppiumBy.XPATH, "//*[contains(@content-desc, 'WhatsApp')]")
            ]

            icon_found = False
            for selector_type, selector in icon_selectors:
                try:
                    whatsapp_element = driver.find_element(selector_type, selector)
                    if whatsapp_element.is_displayed():
                        whatsapp_element.click()
                        time.sleep(1.5)

                        if wait_for_whatsapp_loaded(driver):
                            print(f"[SUCCESS] WhatsApp opened by tapping icon!")
                            return True
                        else:
                            print(f"[FAIL] Icon tap launched but app not properly loaded")
                        icon_found = True
                        break
                except:
                    continue

            if not icon_found:
                print("[FAIL] WhatsApp icon not found on current screen")

        except Exception as e3:
            print(f"[FAIL] Icon tap method failed: {str(e3)}")

        # If this wasn't the last attempt, wait before retrying
        if attempt < max_attempts - 1:
            print(f"[RETRY] All methods failed, waiting before attempt {attempt + 2}...")
            time.sleep(3)

    print("[ERROR] All attempts failed to open WhatsApp properly")
    print("Please ensure:")
    print("1. WhatsApp is installed on the device")
    print("2. Device has sufficient memory")
    print("3. WhatsApp has proper permissions")
    print("4. Device is not in power saving mode")
    return False

def read_daily_message():
    """Read the daily message from the text file"""
    try:
        with open('txt/daily_message.txt', 'r', encoding='utf-8') as file:
            message = file.read().strip()
            if not message:
                print("txt/daily_message.txt is empty. Please add your message to the file.")
                return None
            return message
    except FileNotFoundError:
        print("txt/daily_message.txt not found. Please create the file with your daily message.")
        return None
    except Exception as e:
        print(f"Error reading daily message: {str(e)}")
        return None


def analyze_chat_entries():
    """Analyze txt/chat_name.txt and categorize entries"""
    try:
        with open('txt/chat_name.txt', 'r', encoding='utf-8') as file:
            lines = file.readlines()

        total_entries = 0
        phone_numbers = 0
        groups = 0
        all_entries = []

        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            # Skip empty lines and comments
            if line and not line.startswith('#'):
                # Parse formatted entries like "  - Row 982: NepalWin🇳🇵Shankartr88"
                chat_name = line
                original_row = line_num

                # Check if line has the "- Row X:" format
                if "- Row" in line and ":" in line:
                    parts = line.split(":", 1)
                    if len(parts) == 2:
                        # Extract row number from "- Row 982" part
                        row_part = parts[0].strip()
                        if "Row" in row_part:
                            try:
                                row_number = int(row_part.split("Row")[1].strip())
                                original_row = row_number
                            except:
                                pass  # Keep original line_num if parsing fails

                        # Extract chat name from the part after ":"
                        chat_name = parts[1].strip()

                # Skip if chat name is empty after parsing
                if not chat_name:
                    continue

                all_entries.append((original_row, chat_name))
                total_entries += 1

                # Check if it's a phone number (contains only digits and +)
                clean_for_check = chat_name.replace('NepalWin🇳🇵', '').replace('+', '').replace(' ', '').replace('-', '')
                if clean_for_check.isdigit():
                    phone_numbers += 1
                else:
                    groups += 1

        return {
            'total': total_entries,
            'phones': phone_numbers,
            'groups': groups,
            'entries': all_entries
        }

    except FileNotFoundError:
        print("[ERROR] txt/chat_name.txt not found!")
        return None
    except Exception as e:
        print(f"[ERROR] Error analyzing chat entries: {str(e)}")
        return None

def show_selection_menu(analysis):
    """Show interactive menu for row selection"""
    print("\n" + "="*60)
    print("[TARGET] CHAT TARGETING MENU")
    print("="*60)
    print(f"[STATS] Total entries in file: {analysis['total']} ({analysis['phones']} phones + {analysis['groups']} groups)")
    print()
    print("[TARGET] Row Selection Options:")
    print("1. Process all entries (default)")
    print("2. Start from specific row")
    print("3. Process specific range")
    print("4. Process only first N entries")
    print()

    while True:
        try:
            choice = input("Enter your choice (1-4) or press ENTER for default: ").strip()

            # Default choice (process all)
            if choice == "" or choice == "1":
                return {
                    'mode': 'all',
                    'start': 1,
                    'end': analysis['total'],
                    'entries': analysis['entries']
                }

            # Start from specific row
            elif choice == "2":
                while True:
                    try:
                        start_row = input(f"Enter starting row number (1-{analysis['total']}): ").strip()
                        start_row = int(start_row)
                        if 1 <= start_row <= analysis['total']:
                            selected_entries = analysis['entries'][start_row-1:]
                            print(f"[SUCCESS] Will process {len(selected_entries)} entries starting from row {start_row}")
                            return {
                                'mode': 'start_from',
                                'start': start_row,
                                'end': analysis['total'],
                                'entries': selected_entries
                            }
                        else:
                            print(f"[ERROR] Please enter a number between 1 and {analysis['total']}")
                    except ValueError:
                        print("[ERROR] Please enter a valid number")

            # Process specific range
            elif choice == "3":
                while True:
                    try:
                        start_row = input(f"Enter starting row (1-{analysis['total']}): ").strip()
                        start_row = int(start_row)
                        if not (1 <= start_row <= analysis['total']):
                            print(f"[ERROR] Start row must be between 1 and {analysis['total']}")
                            continue

                        end_row = input(f"Enter ending row ({start_row}-{analysis['total']}): ").strip()
                        end_row = int(end_row)
                        if not (start_row <= end_row <= analysis['total']):
                            print(f"[ERROR] End row must be between {start_row} and {analysis['total']}")
                            continue

                        selected_entries = analysis['entries'][start_row-1:end_row]
                        print(f"[SUCCESS] Will process {len(selected_entries)} entries from row {start_row} to {end_row}")
                        return {
                            'mode': 'range',
                            'start': start_row,
                            'end': end_row,
                            'entries': selected_entries
                        }
                    except ValueError:
                        print("[ERROR] Please enter valid numbers")

            # Process only first N entries
            elif choice == "4":
                while True:
                    try:
                        count = input(f"Enter number of entries to process (1-{analysis['total']}): ").strip()
                        count = int(count)
                        if 1 <= count <= analysis['total']:
                            selected_entries = analysis['entries'][:count]
                            print(f"[SUCCESS] Will process first {count} entries")
                            return {
                                'mode': 'first_n',
                                'start': 1,
                                'end': count,
                                'entries': selected_entries
                            }
                        else:
                            print(f"[ERROR] Please enter a number between 1 and {analysis['total']}")
                    except ValueError:
                        print("[ERROR] Please enter a valid number")

            else:
                print("[ERROR] Please enter 1, 2, 3, 4, or press ENTER for default")

        except KeyboardInterrupt:
            print("\n[ERROR] Operation cancelled by user")
            return None

def load_processed_chats_today():
    """Load list of chats that have already been processed today"""
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = f"txt/processed_chats_{today}.txt"
    
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
    """Transfer photo from PC to Android device with reliable file handling (improved version)"""
    try:
        print(f"[PHOTO] Starting photo transfer for: {local_photo_path}")

        # Validate file exists and get extension
        if not os.path.exists(local_photo_path):
            print(f"[ERROR] Photo file not found: {local_photo_path}")
            return None

        # Get file info
        file_name = os.path.basename(local_photo_path)
        file_ext = os.path.splitext(file_name)[1].lower()
        file_size = os.path.getsize(local_photo_path)
        file_size_mb = file_size / (1024 * 1024)

        print(f"[PHOTO] File: {file_name} ({file_size_mb:.2f}MB)")

        # Validate it's an image file
        valid_extensions = ['.jpg', '.jpeg', '.png', '.webp']
        if file_ext not in valid_extensions:
            print(f"[ERROR] Unsupported file type: {file_ext}. Supported: {valid_extensions}")
            return None

        # Create timestamped filename to avoid conflicts
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        device_filename = f"whatsapp_daily_{timestamp}{file_ext}"
        device_path = f'/sdcard/Pictures/{device_filename}'
        print(f"[PHOTO] Device path: {device_path}")

        # Read the photo file
        try:
            with open(local_photo_path, 'rb') as photo_file:
                photo_data = photo_file.read()
            print(f"[PHOTO] Read {len(photo_data)} bytes from file")
        except Exception as e:
            print(f"[ERROR] Failed to read photo file: {e}")
            return None

        # Check file size limit
        if file_size_mb > 10:
            print(f"[WARNING] Large file size: {file_size_mb:.2f}MB. May take longer to transfer.")

        # Convert to base64 for transfer
        try:
            photo_base64 = base64.b64encode(photo_data).decode('utf-8')
            print(f"[PHOTO] Base64 conversion complete, length: {len(photo_base64)}")
        except Exception as e:
            print(f"[ERROR] Base64 conversion failed: {e}")
            return None

        # Transfer file to device
        start_transfer = time.time()
        try:
            driver.push_file(device_path, photo_base64)
            transfer_time = time.time() - start_transfer
            print(f"[PHOTO] File push completed in {transfer_time:.2f}s")
        except Exception as e:
            transfer_time = time.time() - start_transfer
            print(f"[ERROR] File push failed after {transfer_time:.2f}s: {e}")
            return None

        # Verify transfer success using pull_file (more reliable than shell commands)
        try:
            verify_data = driver.pull_file(device_path)
            if verify_data:
                decoded_data = base64.b64decode(verify_data)
                if len(decoded_data) == file_size:
                    print(f"[SUCCESS] Photo verified on device: {device_path} ({file_size_mb:.2f}MB)")
                    return device_path
                else:
                    print(f"[WARNING] File size mismatch. Expected: {file_size}, Got: {len(decoded_data)}")
                    print(f"[INFO] Photo may still be transferred to: {device_path}")
                    return device_path
            else:
                print(f"[ERROR] Photo transfer verification failed")
                return None
        except Exception as verify_error:
            print(f"[WARNING] Verification failed: {verify_error}")
            print(f"[INFO] Photo transferred to device: {device_path} (verification skipped)")
            return device_path

    except Exception as e:
        print(f"[ERROR] Error transferring photo to device: {str(e)}")
        import traceback
        print(f"[DEBUG] Full error traceback: {traceback.format_exc()}")
        return None

def adaptive_wait(driver, base_delay=1.0, max_delay=5.0):
    """Intelligent delay based on device performance and network conditions"""
    try:
        # Test device responsiveness
        start_time = time.time()
        driver.get_window_size()  # Simple responsiveness test
        response_time = time.time() - start_time

        # Adjust delay based on response time
        if response_time > 0.5:  # Slow device
            delay = min(base_delay * 1.5, max_delay)
            print(f"[DELAY] Slow device detected ({response_time:.2f}s), using {delay:.1f}s delay")
        elif response_time > 0.2:  # Normal device
            delay = base_delay
            print(f"[DELAY] Normal response ({response_time:.2f}s), using {delay:.1f}s delay")
        else:  # Fast device
            delay = max(base_delay * 0.7, 0.3)
            print(f"[DELAY] Fast device ({response_time:.2f}s), using {delay:.1f}s delay")

        time.sleep(delay)
        return delay

    except Exception as e:
        # If test fails, use base delay
        print(f"[DELAY] Responsiveness test failed, using base delay {base_delay}s")
        time.sleep(base_delay)
        return base_delay

def send_message_with_photo(driver, message):
    """Optimized photo + message sending with adaptive delays"""
    start_time = time.time()
    print(f"[INFO] Fast photo + message send...")

    try:
        wait = WebDriverWait(driver, timeout=12, poll_frequency=0.3)  # Increased timeout, adjusted polling
        
        # Step 1: Click attachment button (parallel search with EC.any_of)
        step_start = time.time()
        attachment_selectors = [
            (AppiumBy.ID, "com.whatsapp:id/attach"),
            (AppiumBy.XPATH, "//*[@resource-id='com.whatsapp:id/attach']"),
            (AppiumBy.XPATH, "//android.widget.ImageButton[contains(@resource-id, 'attach')]")
        ]
        
        # Use EC.any_of for parallel search
        attachment_btn = wait.until(
            EC.any_of(
                *[EC.element_to_be_clickable(selector) for selector in attachment_selectors]
            )
        )
        attachment_btn.click()
        adaptive_wait(driver, 0.8, 2.0)  # Adaptive delay
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
        adaptive_wait(driver, 1.0, 2.0)  # Adaptive delay for gallery loading
        print(f"[INFO] Gallery opened ({time.time() - step_start:.2f}s)")
        
        # Step 3: Select first photo with proper element verification
        step_start = time.time()
        try:
            # Wait for gallery to fully load
            time.sleep(.2)

            # Use simple tap on first photo position - more reliable than element selection
            screen_size = driver.get_window_size()

            # Use specific coordinates for photo selection
            photo_x = 180   # Fixed X coordinate
            photo_y = 1350  # Fixed Y coordinate

            print(f"[DEBUG] Screen size: {screen_size['width']}x{screen_size['height']}")
            print(f"[DEBUG] Tapping photo at: ({photo_x}, {photo_y})")

            # Use simple tap instead of W3C actions
            driver.tap([(photo_x, photo_y)])
            adaptive_wait(driver, 0.7, 1.5)  # Adaptive wait for photo selection
            print(f"[INFO] Photo selected via tap ({time.time() - step_start:.2f}s)")

        except Exception as e:
            print(f"[ERROR] Photo selection failed: {e}")
            # Try alternative position
            try:
                photo_x = 180  # Fixed position that usually works
                photo_y = 400
                driver.tap([(photo_x, photo_y)])
                adaptive_wait(driver, 0.7, 1.5)
                print(f"[INFO] Photo selected via fallback tap ({time.time() - step_start:.2f}s)")
            except Exception as e2:
                print(f"[ERROR] All photo selection methods failed: {e2}")
                return False

        # Step 4: Add caption using simple coordinate tap
        step_start = time.time()
        try:
            # Wait for photo preview to load
            adaptive_wait(driver, 0.5, 1.2)

            # Tap on caption area at bottom of screen
            screen_size = driver.get_window_size()
            caption_x = screen_size['width'] // 2  # Center of screen
            caption_y = 2330  # Fixed Y coordinate for caption area

            print(f"[DEBUG] Tapping caption area at: ({caption_x}, {caption_y})")
            driver.tap([(caption_x, caption_y)])
            adaptive_wait(driver, 0.5, 1.0)  # Wait for keyboard to appear
            print(f"[INFO] Caption area tapped ({time.time() - step_start:.2f}s)")

        except Exception as e:
            print(f"[ERROR] Caption tap failed: {e}")
            # Try alternative caption position
            try:
                driver.tap([(360, 1400)])  # Alternative fixed position
                time.sleep(.5)
                print(f"[INFO] Caption area tapped via fallback")
            except:
                print(f"[WARNING] Caption area not accessible, will send without caption")  
        
        # Text input using mobile:type method
        step_start = time.time()
        try:
            # Use mobile:type - reliable and doesn't require adb_shell feature
            driver.execute_script("mobile: type", {"text": message})
            print(f"[INFO] Caption text sent via mobile:type ({time.time() - step_start:.2f}s)")

        except Exception as e:
            print(f"[WARNING] Text input failed, sending photo without caption: {e}")
        
        # Step 5: Send using direct coordinates
        step_start = time.time()
        try:
            print(f"[DEBUG] Using direct coordinate tap for send button...")

            # Use specific coordinates for send button
            send_x = 990   # Fixed X coordinate for send button
            send_y = 2310  # Fixed Y coordinate for send button

            print(f"[DEBUG] Tapping send button at: ({send_x}, {send_y})")
            click_start = time.time()

            driver.tap([(send_x, send_y)])

            click_time = time.time() - click_start
            print(f"[DEBUG] Send button tapped in {click_time:.2f}s")

            time.sleep(0.1)  # Wait for message to send
            print(f"[INFO] Sent ({time.time() - step_start:.2f}s)")

        except Exception as send_error:
            tap_time = time.time() - step_start
            print(f"[ERROR] Send button tap failed after {tap_time:.2f}s: {send_error}")
            raise send_error
        
        total_time = time.time() - start_time
        print(f"[DONE] Photo+message sent! Total: {total_time:.2f}s")
        return True
        
    except Exception as e:
        total_time = time.time() - start_time
        print(f"[ERROR] Error after {total_time:.2f}s: {str(e)}")
        return False



def send_message_to_chat(driver, message):
    """Optimized text message sending - target: under 3 seconds"""
    start_time = time.time()
    print(f"[INFO] Fast text send...")
    
    try:
        wait = WebDriverWait(driver, 2)  # 2 second timeout
        
        # Find message input (faster selectors)
        input_selectors = [
            (AppiumBy.ID, "com.whatsapp:id/entry"),
            (AppiumBy.XPATH, "//*[@resource-id='com.whatsapp:id/entry']"),
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
            (AppiumBy.ID, "com.whatsapp:id/send"),
            (AppiumBy.XPATH, "//*[@resource-id='com.whatsapp:id/send']"),
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
        print(f"[DONE] Text sent! Total: {total_time:.2f}s")
        return True
        
    except Exception as e:
        total_time = time.time() - start_time
        print(f"[ERROR] Error after {total_time:.2f}s: {str(e)}")
        return False

def go_back_to_chat_list(driver):
    """Go back to the main chat list from an individual chat"""
    if not driver:
        print(f"[ERROR] Driver is None, cannot go back to chat list")
        return False

    try:
        # Press back button to return to chat list
        driver.press_keycode(4)  # KEYCODE_BACK
        time.sleep(1.5)
        return True
    except Exception as e:
        print(f"Error going back to chat list: {str(e)}")
        return False


def search_and_find_chat(driver, chat_name):
    """Search for a specific chat using WhatsApp search functionality"""
    search_start = time.time()
    try:
        print(f"Searching for chat: {chat_name}")

        # First, ensure we're on the main WhatsApp screen
        try:
            # print("[DEBUG] Checking if we're on main WhatsApp screen...")
            # Check for WhatsApp main elements
            main_elements = [
                (AppiumBy.XPATH, "//*[@text='WhatsApp']"),
                (AppiumBy.XPATH, "//*[@text='Chats']"),
                (AppiumBy.ID, "com.whatsapp:id/menuitem_search"),
                (AppiumBy.ID, "com.whatsapp:id/search")
            ]

            main_found = False
            for selector in main_elements:
                try:
                    element = driver.find_element(*selector)
                    if element.is_displayed():
                        print(f"[DEBUG] Found main screen element: {selector}")
                        main_found = True
                        break
                except:
                    continue

            if not main_found:
                # print("[DEBUG] Not on main screen, pressing back to return...")
                driver.press_keycode(4)  # Back button
                time.sleep(.5)
        except:
            pass

        # # Look for search button/icon - try multiple selectors with timeout
        # search_selectors = [
        #     # Regular WhatsApp selectors (priority)
        #     (AppiumBy.ID, "com.whatsapp:id/menuitem_search"),
        #     (AppiumBy.ID, "com.whatsapp:id/search"),
        #     (AppiumBy.XPATH, "//*[@resource-id='com.whatsapp:id/menuitem_search']"),
        #     (AppiumBy.XPATH, "//*[@resource-id='com.whatsapp:id/search']"),
        #     # WhatsApp specific selectors (fallback)
        #     (AppiumBy.ID, "com.whatsapp:id/search_bar_inner_layout"),
        #     (AppiumBy.XPATH, "//*[@resource-id='com.whatsapp:id/search_bar_inner_layout']"),
        #     (AppiumBy.ID, "com.whatsapp:id/menuitem_search"),
        #     (AppiumBy.XPATH, "//*[@resource-id='com.whatsapp:id/menuitem_search']"),
        #     # Generic search selectors
        #     (AppiumBy.XPATH, "//*[@content-desc='Search']"),
        #     (AppiumBy.XPATH, "//*[contains(@content-desc, 'Search')]"),
        #     (AppiumBy.XPATH, "//*[@text='Search']")
        # ]

        # wait = WebDriverWait(driver, 3)
        # search_button = None

        # try:
        #     # Use EC.any_of for parallel search of all selectors
        #     search_button = wait.until(
        #         EC.any_of(
        #             *[EC.element_to_be_clickable(selector) for selector in search_selectors]
        #         )
        #     )
        #     print(f"[DEBUG] Found search button using parallel search")
        # except TimeoutException:
        #     print(f"[DEBUG] Search button not found with any of {len(search_selectors)} selectors")

        # if search_button:
        #     # Click on search button
        #     search_button.click()
        #     time.sleep(.5)
        #     print("[DEBUG] Search activated successfully")
        # else:
        #     print("[DEBUG] Search button not found, trying alternative methods...")

        # Wait for search functionality to be ready and activate it
        print("[SEARCH] Activating search...")
        search_activated = False

        # Try WebDriverWait first for search button
        try:
            wait = WebDriverWait(driver, 2)
            search_element = wait.until(EC.element_to_be_clickable((AppiumBy.ID, "com.whatsapp:id/menuitem_search")))
            search_element.click()
            search_activated = True
            print("[SEARCH] Search activated via element click")
        except:
            # Fallback to coordinate tap
            driver.tap([(525, 330)])
            search_activated = True
            print("[SEARCH] Search activated by coordinate tap at (525, 330)")

        if not search_activated:
            print("[ERROR] Failed to activate search")
            return False

        # Wait for search input field to be ready
        time.sleep(1.0)  # Allow search interface to fully load

        # Input Unicode text with better error handling
        try:
            # Wait for search field to be available
            wait = WebDriverWait(driver, 3)
            try:
                search_input = wait.until(EC.element_to_be_clickable((AppiumBy.ID, "com.whatsapp:id/search_src_text")))
                search_input.click()
                search_input.clear()
                search_input.send_keys(chat_name)
                print(f"[SEARCH] Text input via search field element: '{chat_name}'")
            except:
                # Fallback to mobile:type
                driver.execute_script("mobile: type", {"text": chat_name})
                print(f"[SEARCH] Text input via mobile:type: '{chat_name}'")
        except Exception as e:
            print(f"[ERROR] Failed to input search text: {e}")
            return False

        # Enhanced waiting logic with backend loading consideration
        print(f"[WAIT] Waiting for backend to process search results...")
        time.sleep(1.5)  # Initial wait for backend processing
        max_wait_time = 20  # Maximum wait time in seconds
        wait_start = time.time()
        last_message_time = 0  # Track when we last showed a wait message
        messages_section_count = 0  # Track repeated "Messages section exists" messages
        max_repeated_messages = 5  # Exit after 5 repeated messages

        while (time.time() - wait_start) < max_wait_time:
            try:
                # Check #1: PRIORITY - Look for "Chats" section and chat under it FIRST
                try:
                    chats_title = driver.find_element(AppiumBy.XPATH, "//android.widget.TextView[@resource-id='com.whatsapp:id/title' and @text='Chats']")
                    if chats_title.is_displayed():
                        print(f"[FOUND] 'Chats' section located - checking for chat underneath...")

                        # Get the position of the "Chats" section to ensure we look below it
                        chats_location = chats_title.location

                        # Look for chat containers under "Chats" section
                        chat_container_selectors = [
                            (AppiumBy.XPATH, "//android.widget.RelativeLayout[@resource-id='com.whatsapp:id/contact_row_container']"),
                            (AppiumBy.XPATH, "//android.widget.LinearLayout[@resource-id='com.whatsapp:id/contact_row_container']"),
                            (AppiumBy.XPATH, "//*[@resource-id='com.whatsapp:id/contact_row_container']")
                        ]

                        for selector in chat_container_selectors:
                            try:
                                chat_containers = driver.find_elements(*selector)
                                for chat_container in chat_containers:
                                    if chat_container.is_displayed():
                                        # Ensure the chat container is below the "Chats" section
                                        container_location = chat_container.location
                                        if container_location['y'] > chats_location['y']:
                                            # Click on any chat found under "Chats" section (no name matching required)
                                            search_time = time.time() - search_start
                                            print(f"[\033[92mSUCCESS\033[0m] Chat found under 'Chats' section after {search_time:.2f}s")
                                            # Click on the first available chat container
                                            chat_container.click()
                                            print(f"[CLICKED] Opened first available chat")
                                            return True
                            except:
                                continue

                        # If "Chats" section exists but no matching chat found, wait a bit more
                        current_wait_time = time.time() - wait_start
                        if current_wait_time < (max_wait_time * 0.75):  # Give 75% of total wait time
                            print(f"[WAIT] 'Chats' section exists but no matching chat yet - continuing to wait...")
                            time.sleep(0.5)
                            continue
                        else:
                            print(f"[NOT FOUND] 'Chats' section exists but no matching chat found after extended wait")
                            # Don't return False yet, check for standalone "No results" first

                except:
                    pass  # Continue to check for "No results"

                # Check #2: Look for standalone "No results" (ONLY when no sections exist)
                try:
                    # Check if BOTH "Messages" and "Chats" sections are absent
                    message_section_exists = False
                    chats_section_exists = False

                    try:
                        message_section = driver.find_element(AppiumBy.XPATH, "//android.widget.TextView[@resource-id='com.whatsapp:id/title' and @text='Messages']")
                        if message_section.is_displayed():
                            message_section_exists = True
                            messages_section_count += 1
                            if messages_section_count <= 3:  # Only print first 3 times
                                print(f"[DEBUG] 'Messages' section exists - 'No results' under it doesn't mean unavailable")
                            elif messages_section_count == 4:
                                print(f"[DEBUG] 'Messages' section still exists - reducing debug output...")
                    except:
                        pass

                    try:
                        chats_section = driver.find_element(AppiumBy.XPATH, "//android.widget.TextView[@resource-id='com.whatsapp:id/title' and @text='Chats']")
                        if chats_section.is_displayed():
                            chats_section_exists = True
                            print(f"[DEBUG] 'Chats' section exists - still checking for chats")
                    except:
                        pass

                    # Early exit if we've seen "Messages section exists" too many times
                    if messages_section_count >= max_repeated_messages:
                        search_time = time.time() - search_start
                        print(f"[EARLY_EXIT] Seen 'Messages section' {messages_section_count} times with no results - chat likely doesn't exist")
                        print(f"[EARLY_EXIT] Exiting search after {search_time:.2f}s instead of waiting full timeout")
                        # Go back to main screen before returning
                        driver.press_keycode(4)  # Back button
                        time.sleep(0.5)
                        return False

                    # Only consider "No results" as truly unavailable when NO sections exist
                    if not message_section_exists and not chats_section_exists:
                        no_results_selectors = [
                            (AppiumBy.XPATH, "//*[@text='No results found']"),
                            (AppiumBy.XPATH, "//*[contains(@text, 'No results found')]"),
                            (AppiumBy.XPATH, "//*[contains(@text, 'No results')]"),
                            (AppiumBy.XPATH, "//*[@text='No results']")
                        ]

                        for selector in no_results_selectors:
                            try:
                                no_result_element = driver.find_element(*selector)
                                if no_result_element.is_displayed():
                                    search_time = time.time() - search_start
                                    print(f"[\033[91mCONFIRMED\033[0m] Standalone 'No results found' - chat '{chat_name}' truly unavailable after {search_time:.2f}s")
                                    # Go back to main screen before returning
                                    driver.press_keycode(4)  # Back button
                                    time.sleep(0.5)
                                    return False
                            except:
                                continue
                    else:
                        if message_section_exists and messages_section_count <= 3:
                            print(f"[DEBUG] 'Messages' section exists - ignoring any 'No results' under it")
                        if chats_section_exists:
                            print(f"[DEBUG] 'Chats' section exists - continuing to wait for chat")

                except:
                    pass


                # Wait before next check
                time.sleep(0.5)
                elapsed_time = time.time() - wait_start

                # Only show wait message every 3 seconds to reduce spam
                if elapsed_time - last_message_time >= 3.0:
                    #print(f"[WAIT] Still waiting for results... ({elapsed_time:.1f}s / {max_wait_time}s)")
                    last_message_time = elapsed_time

            except Exception as e:
                print(f"[ERROR] Error while waiting: {str(e)}")
                time.sleep(0.5)

        # Timeout reached without finding either condition
        search_time = time.time() - search_start
        print(f"[TIMEOUT] Neither 'No results' nor chat under 'Chats' found after {search_time:.2f}s - assuming not found")
        # Go back to main screen
        driver.press_keycode(4)  # Back button
        time.sleep(0.5)
        return False

    except Exception as e:
        search_time = time.time() - search_start
        print(f"[ERROR] Error searching for chat '{chat_name}' after {search_time:.2f}s: {str(e)}")
        return False

def process_target_chats(driver):
    """Main function to send messages to specific chats listed in txt/chat_name.txt"""
    # Log script start time
    log_script_event("start", "WhatsApp automation script started")

    print("Starting to process target chats from txt/chat_name.txt...")

    # Analyze chat entries and show selection menu
    analysis = analyze_chat_entries()
    if analysis is None:
        print("Failed to analyze chat entries. Stopping automation.")
        return

    # Show interactive selection menu
    selection = show_selection_menu(analysis)
    if selection is None:
        print("No selection made. Stopping automation.")
        return

    # Extract selected chat names (only the chat names, not the line numbers)
    target_chat_names = [entry[1] for entry in selection['entries']]

    print(f"\n[TARGET] Selected Processing Plan:")
    print(f"   - Mode: {selection['mode']}")
    print(f"   - Rows: {selection['start']} to {selection['end']}")
    print(f"   - Total chats to process: {len(target_chat_names)}")
    print(f"   - First few chats: {', '.join(target_chat_names[:3])}{'...' if len(target_chat_names) > 3 else ''}")
    print("="*60)

    # Read the daily message
    daily_message = read_daily_message()
    if daily_message is None:
        print("No message found in txt/daily_message.txt. Stopping automation.")
        return

    print(f"Daily message to send: {daily_message}")

    # Check and transfer daily photo
    photo_path = get_daily_photo_path()
    device_photo_path = None
    send_photo = False

    if photo_path:
        print(f"Found daily photo: {photo_path}")
        print(f"[DEBUG] Attempting to transfer photo to device...")
        device_photo_path = transfer_photo_to_device(driver, photo_path)
        print(f"[DEBUG] Transfer result: {device_photo_path}")
        if device_photo_path:
            send_photo = True
            print("Photo will be sent with each message")
        else:
            print("Photo transfer failed. Will send text messages only.")
    else:
        print("No daily photo found in daily_photos/ folder. Will send text messages only.")

    # Load previously processed chats for today
    processed_chats, log_file = load_processed_chats_today()
    overall_start = time.time()

    successful_chats = []
    failed_chats = []

    print(f"\n[INFO] Starting to process {len(target_chat_names)} target chats")

    for i, (original_row, target_chat_name) in enumerate(selection['entries']):
        chat_processing_start = time.time()

        # Check if driver session is still alive before processing
        if not is_driver_alive(driver):
            print(f"[WARNING] Driver session lost, attempting recovery...")
            recovered_driver = recover_session(driver, max_attempts=3)
            if recovered_driver:
                driver = recovered_driver
                print("[RECOVERY] Session recovered, continuing with automation")
            else:
                print(f"[ERROR] Session recovery failed after multiple attempts, stopping automation")
                break
            # Re-transfer photo if needed after session recovery
            if photo_path and send_photo:
                print(f"[RECOVERY] Re-transferring photo after session recovery...")
                device_photo_path = transfer_photo_to_device(driver, photo_path)
                if not device_photo_path:
                    send_photo = False
                    print("[RECOVERY] Photo re-transfer failed, will send text only")

        # Skip if already processed today
        if target_chat_name in processed_chats:
            print(f"[\033[92m{i+1}/{len(target_chat_names)}\033[0m] [SKIP] Already processed today: {target_chat_name} (Row {original_row})")
            continue

        print(f"\n[\033[92m{i+1}/{len(target_chat_names)}\033[0m] Processing: {target_chat_name} (Row {original_row})")

        # Clean the chat name (remove prefix) before searching
        clean_name = clean_chat_name(target_chat_name)

        # Search for the specific chat using search functionality with enhanced error handling
        search_start = time.time()
        try:
            chat_found = safe_operation(search_and_find_chat, driver, clean_name, retry_count=1)
        except Exception as search_error:
            print(f"[ERROR] Search function failed: {search_error}")
            # Try session recovery if it's a driver-related error
            driver_errors = ["session", "connection", "socket", "timeout", "network"]
            if any(error_term in str(search_error).lower() for error_term in driver_errors):
                print("[ERROR] Detected driver-related error, attempting session recovery...")
                recovered_driver = recover_session(driver, max_attempts=2)
                if recovered_driver:
                    driver = recovered_driver
                    print("[RECOVERY] Retrying search after session recovery...")
                    try:
                        chat_found = search_and_find_chat(driver, clean_name)
                    except Exception as retry_error:
                        print(f"[ERROR] Search retry failed: {retry_error}")
                        chat_found = False
                else:
                    print("[ERROR] Session recovery failed")
                    chat_found = False
            else:
                chat_found = False
        search_time = time.time() - search_start

        if chat_found:
            try:
                # Chat is already opened by search_and_find_chat function
                # Send the daily message (with photo if available)
                message_start = time.time()
                try:
                    if send_photo:
                        success = send_message_with_photo(driver, daily_message)
                    else:
                        success = send_message_to_chat(driver, daily_message)
                except Exception as message_error:
                    print(f"[ERROR] Message sending failed: {message_error}")
                    # Check if it's a session error
                    if not is_driver_alive(driver):
                        print(f"[WARNING] Session lost during message sending, attempting recovery...")
                        driver = recover_session(driver)
                        if driver:
                            # Try to find and open the chat again
                            chat_found_retry = search_and_find_chat(driver, clean_name)
                            if chat_found_retry:
                                try:
                                    if send_photo:
                                        success = send_message_with_photo(driver, daily_message)
                                    else:
                                        success = send_message_to_chat(driver, daily_message)
                                except:
                                    success = False
                            else:
                                success = False
                        else:
                            success = False
                    else:
                        success = False
                message_time = time.time() - message_start

                if success:
                    message_type = "message + photo" if send_photo else "message"
                    print(f"[SUCCESS] Successfully sent {message_type} to: {target_chat_name} (Row {original_row})")
                    successful_chats.append((original_row, target_chat_name))
                    processed_chats.add(target_chat_name)
                    save_processed_chat(log_file, f"Row{original_row}: {target_chat_name}")
                else:
                    message_type = "message + photo" if send_photo else "message"
                    print(f"[ERROR] Failed to send {message_type} to: {target_chat_name} (Row {original_row})")
                    failed_chats.append((original_row, target_chat_name))
                    processed_chats.add(target_chat_name)
                    save_processed_chat(log_file, f"FAILED Row{original_row}: {target_chat_name}")

                # Go back to chat list
                back_start = time.time()
                print(f"🔙 Going back to chat list...")
                if driver:  # Check if driver is not None
                    try:
                        driver.press_keycode(4)  # KEYCODE_BACK
                        time.sleep(1)
                        back_time = time.time() - back_start
                        print(f"[CHECKED] Returned to chat list in {back_time:.2f}s")
                    except Exception as back_error:
                        print(f"[ERROR] Failed to go back to chat list: {back_error}")
                        back_time = time.time() - back_start
                        # Try session recovery
                        driver = recover_session(driver)
                        if not driver:
                            print(f"[ERROR] Session recovery failed, stopping automation")
                            break
                else:
                    print(f"[ERROR] Driver is None, cannot go back to chat list")
                    back_time = time.time() - back_start

                total_chat_time = time.time() - chat_processing_start
                print(f"[TIME] Total time for {target_chat_name}: {total_chat_time:.2f}s")
                print(f"   - Search + open: {search_time:.2f}s")
                print(f"   - Message sending: {message_time:.2f}s")
                print(f"   - Back to list: {back_time:.2f}s")
                print("─" * 60)

            except Exception as e:
                print(f"[ERROR] Error processing chat '{target_chat_name}' (Row {original_row}): {str(e)}")
                failed_chats.append((original_row, target_chat_name))
                go_back_to_chat_list(driver)
                continue
        else:
            search_time = time.time() - search_start
            if clean_name != target_chat_name:
                print(f"[ERROR] Chat '{target_chat_name}' (searched as '{clean_name}') not found after {search_time:.2f}s ")
            else:
                print(f"[ERROR] Chat '{target_chat_name}' not found after {search_time:.2f}s ")

            # Log the not found chat with GMT+7 timestamp
            log_not_found_chat(target_chat_name, original_row)

            failed_chats.append((original_row, target_chat_name))
            processed_chats.add(target_chat_name)
            save_processed_chat(log_file, f"NOT_FOUND Row{original_row}: {target_chat_name}")

            print(f"[NEXT] Quickly moving to next chat...")
            continue

    overall_time = time.time() - overall_start
    print(f"\n[INFO] Processing complete! Total time: {overall_time:.2f}s")
    print(f"[INFO] Summary:")
    print(f"   - Total target chats: {len(target_chat_names)}")
    print(f"   - Successfully processed: {len(successful_chats)}")
    print(f"   - Failed/Not found: {len(failed_chats)}")
    print(f"   - Average time per chat: {overall_time/len(target_chat_names):.2f}s")

    if successful_chats:
        print(f"\n[SUCCESS] Successfully sent messages to {len(successful_chats)} chats:")
        for row, chat_name in successful_chats:
            print(f"  - Row {row}: {chat_name}")

    if failed_chats:
        print(f"\n[ERROR] Failed to process {len(failed_chats)} chats:")
        for row, chat_name in failed_chats:
            print(f"  - Row {row}: {chat_name}")

    # Log script end time with summary
    summary_message = f"Script completed - Processed: {len(successful_chats)}, Failed: {len(failed_chats)}, Total time: {overall_time:.2f}s"
    log_script_event("end", summary_message)

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
            
            # Open WhatsApp after successful unlock
            whatsapp_success = open_whatsapp_business(driver)
            
            if whatsapp_success:
                print("WhatsApp is now open and ready for use!")
                # Brief pause to ensure app is fully loaded
                time.sleep(1.8)
                
                # Process target chats from txt/chat_name.txt and send daily messages
                process_target_chats(driver)
                
            else:
                print("Failed to open WhatsApp, but device is unlocked")
            
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
    print("* Press Ctrl+C to stop the automation at any time")
    print("   (Note: On macOS terminal, use Ctrl+C, not Cmd+C)")
    main()