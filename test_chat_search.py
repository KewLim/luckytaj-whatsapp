#!/usr/bin/env python3

from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import signal
import sys

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

def find_next_chat_without_unread(driver, start_position=1):
    """Find the first chat without unread messages starting from given position up to 7"""
    search_start = time.time()
    print(f"[INFO] Searching for chats without unread messages (positions {start_position}-7)...")
    
    try:
        wait = WebDriverWait(driver, timeout=5, poll_frequency=0.2)
        
        # Check from start_position to 7
        chat_position = start_position
        max_chats_to_check = 7
        last_chat_name = None
        
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
                    if chat_position == 1:
                        print(f"❌ No chats found at all - reached end of chat list")
                        return None, None, None, "END_OF_LIST"
                    else:
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
                
                # Record the last chat seen (always update)
                last_chat_name = chat_name
                
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
                    return chat_container, chat_name, chat_position, last_chat_name
                
            except Exception as e:
                print(f"❌ Error checking position [{chat_position}]: {str(e)}")
                chat_position += 1
                continue
        
        total_time = time.time() - search_start
        if last_chat_name:
            print(f"❌ No chats without unread messages found after checking positions {start_position}-{chat_position-1} (total time: {total_time:.2f}s)")
            return None, None, None, last_chat_name
        else:
            print(f"❌ No chats found at all - reached end of chat list (total time: {total_time:.2f}s)")
            return None, None, None, "END_OF_LIST"
        
    except Exception as e:
        total_time = time.time() - search_start
        print(f"❌ Error finding chats after {total_time:.2f}s: {str(e)}")
        return None, None, None, "ERROR"

def process_whatsapp_chats(driver, send_message_callback=None, scroll_percent=0.25, sleep_time=0.3):
    """
    Continuously process WhatsApp chats without unread messages.
    
    :param driver: Appium driver
    :param send_message_callback: function(chat_element) called when a chat is processed
    :param scroll_percent: percent of swipe when scrolling
    :param sleep_time: time to wait after swipe
    """
    processed_chats = set()

    while True:
        # 1. Get currently visible chats
        chat_containers = driver.find_elements(
            AppiumBy.XPATH, "//android.widget.LinearLayout[@resource-id='com.whatsapp.w4b:id/contact_row_container']"
        )

        if not chat_containers:
            break  # no chats visible

        last_chat = None
        last_chat_name = None

        # 2. Iterate through visible chats, track 7th chat for scrolling
        seventh_chat_name = None
        processed_count = 0
        
        for i, chat in enumerate(chat_containers):
            # Get chat name from the chat container
            try:
                chat_name_element = chat.find_element(
                    AppiumBy.XPATH, ".//android.widget.TextView[contains(@resource-id, 'conversations_row_contact_name')]"
                )
                chat_name = chat_name_element.text
            except NoSuchElementException:
                continue
                
            # Track the 7th chat name (index 6) but DON'T process it
            if i == 6:  # 7th chat (0-indexed)
                seventh_chat_name = chat_name
                print(f"📍 Tracking 7th chat: {chat_name} - will scroll to make it first")
                break  # Stop processing, time to scroll
                
            if chat_name in processed_chats:
                continue

            # Skip chats with unread messages
            try:
                chat.find_element(
                    AppiumBy.XPATH, ".//android.view.View[contains(@content-desc, 'unread message')]"
                )
                continue
            except NoSuchElementException:
                pass

            # Process chat (only positions 1-6)
            chat.click()
            if send_message_callback:
                # Create a mock element with the chat name to avoid stale element issues
                class MockChat:
                    def __init__(self, name):
                        self._name = name
                    def get_attribute(self, attr):
                        return self._name
                send_message_callback(MockChat(chat_name))
            driver.back()
            
            processed_chats.add(chat_name)
            last_chat = chat
            last_chat_name = chat_name  # Store the name before element becomes stale
            processed_count += 1

        if processed_count == 0:
            print("❌ No new chats processed, breaking")
            break

        # Make sure we're back to the chat list before scrolling
        print("🔙 Going back to chat list before scrolling...")
        driver.back()
        time.sleep(0.5)  # Wait for list to load

        # 3. Scroll exactly 6 positions so 7th chat becomes 1st (instead of scrolling until last becomes first)
        if seventh_chat_name:
            print(f"Scrolling 6 positions to move '{seventh_chat_name}' to first position...")
            
            # Perform exactly 6 scroll movements
            for scroll_step in range(6):
                visible_chats = driver.find_elements(
                    AppiumBy.XPATH, "//android.widget.LinearLayout[@resource-id='com.whatsapp.w4b:id/contact_row_container']"
                )
                if not visible_chats:
                    print(f"No visible chats during scroll step {scroll_step + 1}, trying screen swipe...")
                    size = driver.get_window_size()
                    start_x = size['width'] // 2
                    start_y = int(size['height'] * 0.8)
                    end_y = int(size['height'] * 0.2)
                    driver.swipe(start_x, start_y, start_x, end_y, duration=500)
                    time.sleep(sleep_time)
                    continue

                try:
                    # Scroll one position at a time using the bottom chat
                    driver.execute_script(
                        "mobile: swipeGesture",
                        {
                            "elementId": visible_chats[-1].id,
                            "direction": "up",
                            "percent": scroll_percent
                        }
                    )
                except:
                    # Fallback to screen swipe if element swipe fails
                    size = driver.get_window_size()
                    start_x = size['width'] // 2
                    start_y = int(size['height'] * 0.8)
                    end_y = int(size['height'] * 0.2)
                    driver.swipe(start_x, start_y, start_x, end_y, duration=500)
                
                time.sleep(sleep_time)
                print(f"Scroll step {scroll_step + 1}/6 completed")
            
            print(f"✅ Scrolled 6 positions, '{seventh_chat_name}' should now be first visible")
        else:
            print("⚠️ No 7th chat found, using fallback scroll method...")
            # Fallback: scroll using screen coordinates
            size = driver.get_window_size()
            start_x = size['width'] // 2
            start_y = int(size['height'] * 0.8)
            end_y = int(size['height'] * 0.2)
            for _ in range(6):
                driver.swipe(start_x, start_y, start_x, end_y, duration=500)
                time.sleep(sleep_time)

def process_whatsapp_chats_test(driver, send_message_callback=None, sleep_time=0.3, max_scroll_attempts=10):
    """
    Test version: Process WhatsApp chats (ignoring unread messages) to test scrolling logic.
    """
    processed_chats = set()
    max_chats_to_process = 5  # Limit for testing

    def scroll_last_chat_to_top(last_chat):
        """
        Scroll until the last_chat becomes the first visible chat using screen swipe.
        Returns True if successful, False if max attempts reached.
        """
        try:
            # Try to get the chat name, but handle stale element
            last_chat_name = last_chat.find_element(
                AppiumBy.XPATH, ".//android.widget.TextView[contains(@resource-id, 'conversations_row_contact_name')]"
            ).text
            print(f"Scrolling until '{last_chat_name}' becomes first visible")
        except:
            print("Could not get last chat name (stale element), using generic scroll")
            last_chat_name = None

        attempts = 0
        while attempts < max_scroll_attempts:
            # If we don't have the last chat name, just scroll a few times
            if last_chat_name is None:
                print(f"Generic scroll attempt {attempts + 1}")
                # Just scroll a reasonable amount
                if attempts >= 3:  # Only do 3 generic scrolls
                    return True
            else:
                try:
                    top_chat_name = driver.find_element(
                        AppiumBy.XPATH, "//android.widget.LinearLayout[@resource-id='com.whatsapp.w4b:id/contact_row_container'][1]//android.widget.TextView[contains(@resource-id, 'conversations_row_contact_name')]"
                    ).text
                except:
                    print("Could not get top chat name")
                    break

                if top_chat_name == last_chat_name:
                    print(f"✅ '{last_chat_name}' is now the top chat")
                    return True

            # Swipe up using screen coordinates
            size = driver.get_window_size()
            start_x = size['width'] // 2
            start_y = int(size['height'] * 0.8)
            end_y = int(size['height'] * 0.2)
            driver.swipe(start_x, start_y, start_x, end_y, duration=500)

            time.sleep(sleep_time)
            attempts += 1
            print(f"Scrolling... attempt {attempts}")

        print("❌ Max scroll attempts reached")
        return False

    while len(processed_chats) < max_chats_to_process:
        # 1. Get currently visible chats (re-find each time to avoid stale elements)
        try:
            chat_containers = driver.find_elements(
                AppiumBy.XPATH, "//android.widget.LinearLayout[@resource-id='com.whatsapp.w4b:id/contact_row_container']"
            )
        except Exception as e:
            print(f"Error finding chat containers: {e}")
            break

        if not chat_containers:
            print("No chats found, breaking")
            break

        print(f"Found {len(chat_containers)} chats on current view")
        last_chat_name_for_scroll = None
        processed_in_this_round = 0

        # 2. Iterate through visible chats
        for i, chat in enumerate(chat_containers):
            try:
                chat_name_element = chat.find_element(
                    AppiumBy.XPATH, ".//android.widget.TextView[contains(@resource-id, 'conversations_row_contact_name')]"
                )
                chat_name = chat_name_element.text
            except Exception:
                continue
                
            if chat_name in processed_chats:
                print(f"Already processed: {chat_name}")
                continue

            # Skip chats with unread messages
            try:
                chat.find_element(
                    AppiumBy.XPATH, ".//android.view.View[contains(@content-desc, 'unread message')]"
                )
                print(f"⏭️ Skipping {chat_name} - has unread messages")
                continue
            except NoSuchElementException:
                pass

            print(f"Processing chat: {chat_name}")
            try:
                chat.click()
                if send_message_callback:
                    # Create a mock element with the chat name to avoid stale element issues
                    class MockChat:
                        def __init__(self, name):
                            self._name = name
                        def get_attribute(self, attr):
                            return self._name
                    send_message_callback(MockChat(chat_name))
                driver.back()
                time.sleep(0.5)  # Wait for list to stabilize
                
                processed_chats.add(chat_name)
                last_chat_name_for_scroll = chat_name  # Store name, not element
                processed_in_this_round += 1
                
                if len(processed_chats) >= max_chats_to_process:
                    break
            except Exception as e:
                print(f"Error processing chat {chat_name}: {e}")
                continue

        if processed_in_this_round == 0:
            print("No new chats processed, breaking")
            break

        # 3. Scroll using generic screen swipe (avoid using stale elements)
        if last_chat_name_for_scroll:
            print(f"Scrolling after processing. Last chat was: {last_chat_name_for_scroll}")
            
            # Generic scroll - just scroll down a bit to show more chats
            for scroll_attempt in range(3):
                size = driver.get_window_size()
                start_x = size['width'] // 2
                start_y = int(size['height'] * 0.8)
                end_y = int(size['height'] * 0.2)
                driver.swipe(start_x, start_y, start_x, end_y, duration=500)
                time.sleep(sleep_time)
                print(f"Generic scroll {scroll_attempt + 1}/3 completed")


def send_message_callback(chat_element):
    """Callback function for processing each chat"""
    try:
        # Handle both real elements and mock elements
        if hasattr(chat_element, 'get_attribute'):
            chat_name = chat_element.get_attribute("content-desc") 
        elif hasattr(chat_element, '_name'):
            chat_name = chat_element._name  # Mock element
        else:
            chat_name = "Unknown"
    except:
        chat_name = "Unknown"
    
    print(f"🎯 Processing chat: {chat_name}")
    time.sleep(2)
    print(f"✅ Successfully processed chat: {chat_name}")

def test_chat_search():
    """Main test function to test chat search functionality with scrolling"""
    driver = None
    
    try:
        # Set up signal handler for graceful exit
        signal.signal(signal.SIGINT, signal_handler)
        
        print("🔧 Setting up Appium driver...")
        driver = setup_driver()
        
        # Turn on screen and unlock
        if not turn_screen_on_and_unlock(driver):
            print("❌ Failed to unlock device")
            return
        
        # Launch WhatsApp Business
        if not open_whatsapp_business(driver):
            print("❌ Failed to launch WhatsApp Business")
            return
        
        # Add initial setup from main WhatsApp script
        print("WhatsApp Business is now open and ready for use!")
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
        
        # Use the new process_whatsapp_chats function
        print("\n" + "="*50)
        print("🔍 STARTING WHATSAPP CHAT PROCESSING WITH NEW SCROLLING LOGIC")
        print("="*50)
        
        try:
            process_whatsapp_chats_test(driver, send_message_callback)
            print(f"\n✅ Chat processing COMPLETED!")
        except Exception as e:
            print(f"\n❌ Error during chat processing: {str(e)}")
        
        print("\n" + "="*50)
        print("🏁 TEST COMPLETE")
        print("="*50)
        
    except Exception as e:
        print(f"❌ Error in test: {str(e)}")
    finally:
        if driver:
            print("🧹 Cleaning up driver...")
            driver.quit()

if __name__ == "__main__":
    test_chat_search()