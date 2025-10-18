#!/usr/bin/env python3

from appium.webdriver.webdriver import WebDriver
from appium.options.android.uiautomator2.base import UiAutomator2Options
from selenium.webdriver.common.by import By as AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import os
import signal
import sys
from datetime import datetime

# Global variable to track the driver for cleanup
_global_driver = None

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n\n🛑 Stopping scraper (Ctrl+C pressed)...")
    print("Cleaning up...")

    global _global_driver
    if _global_driver:
        try:
            print("Closing Appium session...")
            _global_driver.quit()
            print("Session closed successfully")
        except Exception as e:
            print(f"Error closing session: {e}")

    print("Scraper stopped. Goodbye!")
    sys.exit(0)

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

def open_whatsapp(driver):
    """Open WhatsApp application - optimized for speed"""
    try:
        print("Opening WhatsApp...")

        # Method 1: Use activate_app first (most reliable and fastest)
        driver.activate_app("com.whatsapp")
        time.sleep(.5)  # Reduced wait time
        print("WhatsApp opened using activate_app!")
        return True

    except Exception as e:
        print(f"Failed to open WhatsApp with activate_app: {str(e)}")

        try:
            # Method 2: Try start_activity as fallback
            driver.start_activity("com.whatsapp", "com.whatsapp.home.ui.HomeActivity")
            time.sleep(1.5)

            print("WhatsApp opened using start_activity!")
            return True

        except Exception as e2:
            print(f"Failed to open WhatsApp with start_activity: {str(e2)}")

            try:
                # Method 3: Find and tap WhatsApp icon (faster search)
                print("Searching for WhatsApp icon...")

                # Try multiple possible text variations
                possible_texts = ["WhatsApp", "WA"]

                for text in possible_texts:
                    try:
                        whatsapp_element = driver.find_element(AppiumBy.XPATH, f"//android.widget.TextView[@text='{text}']")
                        whatsapp_element.click()
                        time.sleep(.5)
                        print(f"WhatsApp opened by clicking '{text}' icon!")
                        return True
                    except:
                        continue

                print("WhatsApp icon not found on current screen")
                return False

            except Exception as e3:
                print(f"All methods failed to open WhatsApp: {str(e3)}")
                print("Please ensure WhatsApp is installed on the device")
                return False

def is_group_chat(chat_element, chat_name):
    """Detect if a chat is a group chat based on various indicators"""
    try:
        # Method 1: Look for group indicators in the chat element
        group_indicators = [
            "//android.widget.ImageView[contains(@content-desc, 'group')]",
            "//*[contains(@resource-id, 'group')]",
            "//android.widget.TextView[contains(text(), 'participants')]"
        ]

        for indicator in group_indicators:
            try:
                if chat_element.find_element(AppiumBy.XPATH, indicator):
                    return True
            except:
                continue

        # Method 2: Name-based detection (common patterns)
        group_patterns = [
            # Common group naming patterns
            lambda name: len(name.split()) >= 3,  # Groups often have longer names
            lambda name: any(word in name.lower() for word in ['group', 'team', 'family', 'friends', 'class', 'work']),
            lambda name: not name.replace('+', '').replace(' ', '').replace('-', '').isdigit()  # Not a phone number
        ]

        group_score = sum(1 for pattern in group_patterns if pattern(chat_name))

        # If 2 or more indicators suggest it's a group, classify as group
        return group_score >= 2

    except:
        # Default to individual if detection fails
        return False

def wait_for_chat_list_loaded(driver, timeout=10):
    """Wait for WhatsApp chat list to be fully loaded"""
    print("[LOAD] Waiting for chat list to load...")

    # Wait for main WhatsApp elements to appear
    wait = WebDriverWait(driver, timeout)

    try:
        # Look for main WhatsApp indicators
        main_indicators = [
            (AppiumBy.XPATH, "//*[@text='Chats']"),
            (AppiumBy.XPATH, "//*[@text='WhatsApp']"),
            (AppiumBy.ID, "com.whatsapp:id/fab"),
            (AppiumBy.ID, "com.whatsapp:id/menuitem_search")
        ]

        element_found = False
        for selector_type, selector in main_indicators:
            try:
                element = wait.until(EC.presence_of_element_located((selector_type, selector)))
                if element.is_displayed():
                    print(f"[LOAD] Found main WhatsApp element: {selector}")
                    element_found = True
                    break
            except TimeoutException:
                continue

        if not element_found:
            print("[LOAD] No main WhatsApp elements found!")
            return False

        # Additional wait for chat list to populate
        print("[LOAD] Main elements found, waiting for chat list to populate...")
        time.sleep(3)  # Allow time for chats to load

        return True

    except Exception as e:
        print(f"[LOAD] Error waiting for chat list: {e}")
        return False

def debug_current_screen(driver):
    """Debug function to analyze current screen state"""
    try:
        print("\n[DEBUG] === SCREEN ANALYSIS ===")

        # Get all elements on screen
        all_elements = driver.find_elements(AppiumBy.XPATH, "//*")
        print(f"[DEBUG] Total elements found: {len(all_elements)}")

        # Look for any text elements
        text_elements = driver.find_elements(AppiumBy.XPATH, "//android.widget.TextView")
        print(f"[DEBUG] Text elements found: {len(text_elements)}")

        # Print first 10 text elements
        for i, element in enumerate(text_elements[:10]):
            try:
                text = element.text
                if text and text.strip():
                    print(f"[DEBUG] Text {i+1}: '{text}'")
            except:
                continue

        # Look specifically for common WhatsApp elements
        whatsapp_indicators = [
            "WhatsApp", "Chats", "Status", "Calls", "Search", "New chat", "Menu"
        ]

        for indicator in whatsapp_indicators:
            try:
                elements = driver.find_elements(AppiumBy.XPATH, f"//*[@text='{indicator}']")
                if elements:
                    print(f"[DEBUG] Found '{indicator}' elements: {len(elements)}")
            except:
                continue

        print("[DEBUG] === END SCREEN ANALYSIS ===\n")

    except Exception as e:
        print(f"[DEBUG] Screen analysis failed: {e}")

def scrape_all_chat_names(driver):
    """Scrape all chat names from WhatsApp main screen with scrolling"""
    try:
        print("Starting to scrape all chat names...")

        # Check if we're already on the main WhatsApp screen before pressing back
        try:
            # Look for main WhatsApp indicators first
            main_screen_indicators = [
                (AppiumBy.XPATH, "//*[@text='Chats']"),
                (AppiumBy.XPATH, "//*[@text='WhatsApp']"),
                (AppiumBy.ID, "com.whatsapp:id/fab"),
                (AppiumBy.ID, "com.whatsapp:id/menuitem_search")
            ]

            on_main_screen = False
            for selector_type, selector in main_screen_indicators:
                try:
                    element = driver.find_element(selector_type, selector)
                    if element.is_displayed():
                        print(f"[SCREEN] Already on main screen - found: {selector}")
                        on_main_screen = True
                        break
                except:
                    continue

            # Only press back if we're NOT on the main screen
            if not on_main_screen:
                print("[SCREEN] Not on main screen, pressing back to navigate there...")
                driver.press_keycode(4)  # Back button to ensure main screen
                time.sleep(1.5)
            else:
                print("[SCREEN] Already on main WhatsApp screen, proceeding with scraping")

        except Exception as e:
            print(f"[SCREEN] Screen check failed: {e}")
            # Don't press back if we can't determine screen state

        # Wait for chat list to be fully loaded
        if not wait_for_chat_list_loaded(driver):
            print("[ERROR] Chat list failed to load properly")
            debug_current_screen(driver)
            return []

        # Click on "Groups" tab to filter only group chats
        try:
            print("[FILTER] Clicking on 'Groups' tab to show only group chats...")

            # Try different selectors for the Groups tab
            groups_selectors = [
                # Primary selectors
                (AppiumBy.XPATH, "//*[@text='Groups']"),
                (AppiumBy.XPATH, "//android.widget.TextView[@text='Groups']"),

                # UiSelector-based selectors (your recommendation)
                (AppiumBy.XPATH, "//*[contains(@content-desc, 'Groups filter')]"),
                (AppiumBy.XPATH, "//*[contains(@content-desc, 'Groups filter') and contains(@content-desc, 'unselected')]"),

                # Fallback selectors
                (AppiumBy.XPATH, "//*[contains(@text, 'Groups')]"),
                (AppiumBy.XPATH, "//android.widget.Button[@text='Groups']")
            ]

            groups_clicked = False
            for selector_type, selector in groups_selectors:
                try:
                    groups_element = driver.find_element(selector_type, selector)
                    if groups_element.is_displayed():
                        groups_element.click()
                        groups_clicked = True
                        print("[FILTER] Successfully clicked 'Groups' tab")
                        break
                except:
                    continue

            if not groups_clicked:
                print("[FILTER] Groups tab not found, will scrape all chats")
            else:
                # Wait for groups filter to take effect
                time.sleep(2)
                print("[FILTER] Now showing only group chats")

        except Exception as e:
            print(f"[FILTER] Failed to click Groups tab: {e}")
            print("[FILTER] Will scrape all chats instead")

        all_chats = []
        seen_chats = set()
        seen_positions = set()  # Track element positions to avoid duplicates
        scroll_attempts = 0
        max_scrolls = 30  # Reduced from 50 to prevent excessive scrolling
        consecutive_empty_scrolls = 0
        last_scroll_position = None  # Track scroll position to detect when we've reached the end
        last_processed_elements = []  # Track elements from previous iteration

        while scroll_attempts < max_scrolls and consecutive_empty_scrolls < 3:
            print(f"[SCROLL] Attempt {scroll_attempts + 1}/{max_scrolls}")

            # Find all chat elements on current screen
            chat_elements = []

            # Use the working selector (selector 2 from your output)
            working_selector = "//android.widget.LinearLayout[@resource-id='com.whatsapp:id/contact_row_container']"

            try:
                all_current_elements = driver.find_elements(AppiumBy.XPATH, working_selector)
                print(f"[DEBUG] Found {len(all_current_elements)} total chat elements using working selector")
            except Exception as e:
                print(f"[DEBUG] Working selector failed: {e}")
                all_current_elements = []

            # If still no elements found, do detailed debugging
            if not all_current_elements:
                print("[DEBUG] No chat elements found - analyzing screen...")
                debug_current_screen(driver)

            # Smart element filtering: skip elements we've already processed
            chat_elements = []
            if scroll_attempts == 0:
                # First iteration: process all elements
                chat_elements = all_current_elements
                print(f"[SMART] First iteration: processing all {len(chat_elements)} elements")
            else:
                # Subsequent iterations: find new elements by comparing positions
                current_positions = []
                for element in all_current_elements:
                    try:
                        pos = element.location
                        position_key = f"{pos['x']},{pos['y']}"
                        current_positions.append((position_key, element))
                    except:
                        continue

                # Filter out elements we've seen before
                new_elements = []
                overlap_count = 0
                for pos_key, element in current_positions:
                    if pos_key not in seen_positions:
                        new_elements.append(element)
                        seen_positions.add(pos_key)
                    else:
                        overlap_count += 1

                chat_elements = new_elements
                print(f"[SMART] Found {len(chat_elements)} new elements (skipped {overlap_count} already processed)")

                # If we found very few new elements, we might be at the end
                if len(new_elements) <= 2 and len(all_current_elements) >= 5:
                    print(f"[SMART] Very few new elements found, likely near end of list")

            current_screen_chats = []

            # Extract chat names from filtered elements
            for i, element in enumerate(chat_elements):
                try:
                    # Use selector_2 which worked (TextView position 2)
                    working_name_selector = ".//android.widget.TextView[2]"

                    chat_name = None
                    try:
                        name_element = element.find_element(AppiumBy.XPATH, working_name_selector)
                        potential_name = name_element.text.strip()

                        # Filter out timestamps, status messages, and system elements
                        excluded_patterns = [
                            ":", "PM", "AM", "/", "You're now an admin", "left", "joined",
                            "WhatsApp", "Search", "New chat", "Chats", "Status", "Calls"
                        ]

                        is_valid_chat_name = (
                            potential_name and
                            len(potential_name) > 1 and
                            not any(pattern in potential_name for pattern in excluded_patterns) and
                            not potential_name.isdigit() and  # Not just numbers
                            not potential_name.replace(":", "").replace(" ", "").replace("/", "").isdigit()  # Not date/time
                        )

                        if is_valid_chat_name:
                            chat_name = potential_name

                    except Exception as name_error:
                        pass  # Element might not have the expected structure

                    if chat_name and chat_name not in seen_chats:
                        # All chats are groups since we clicked the Groups tab
                        chat_info = {
                            'name': chat_name,
                            'type': 'group',  # All are groups after filtering
                            'position': len(all_chats) + 1
                        }

                        all_chats.append(chat_info)
                        current_screen_chats.append(chat_name)
                        seen_chats.add(chat_name)

                        # Real-time print of each group chat found
                        print(f"[GROUP] #{chat_info['position']:2d}: {chat_name}")

                except Exception as e:
                    continue

            print(f"[FOUND] {len(current_screen_chats)} new chats on this screen")
            if current_screen_chats:
                for chat in current_screen_chats:
                    print(f"  - {chat}")
                consecutive_empty_scrolls = 0
            else:
                consecutive_empty_scrolls += 1

            # Store information about this iteration
            last_processed_elements = chat_elements
            iteration_info = {
                'total_elements_found': len(all_current_elements),
                'new_elements_processed': len(chat_elements),
                'new_chats_found': len(current_screen_chats)
            }

            print(f"[INFO] Iteration summary: {iteration_info['total_elements_found']} total elements, "
                  f"{iteration_info['new_elements_processed']} new elements, "
                  f"{iteration_info['new_chats_found']} new chats")

            # Smart scrolling decision based on elements found
            should_scroll = False

            # Decide whether to scroll based on multiple factors
            if not current_screen_chats:
                if iteration_info['new_elements_processed'] > 0:
                    print("[SCROLL] Found new elements but no valid chats - continuing to scroll")
                    should_scroll = True
                else:
                    print("[SCROLL] No new elements or chats found")
                    consecutive_empty_scrolls += 1
                    if consecutive_empty_scrolls < 2:  # Give it another chance
                        should_scroll = True

            elif len(current_screen_chats) >= 3:  # Found good number of chats
                print("[SCROLL] Found good number of chats - continuing to scroll for more")
                should_scroll = True

            elif iteration_info['total_elements_found'] >= 8:  # Screen still has many elements
                print("[SCROLL] Screen still has many elements - continuing to scroll")
                should_scroll = True

            else:
                print("[SCROLL] Few chats found and screen has few elements - might be near end")
                should_scroll = True  # But will rely on other stop conditions

            if should_scroll and consecutive_empty_scrolls < 3:
                print("[SCROLL] Scrolling down for more chats...")

                # Perform smaller scroll to avoid missing chats
                screen_size = driver.get_window_size()
                start_y = screen_size['height'] * 0.7   # Start higher
                end_y = screen_size['height'] * 0.4     # End lower
                center_x = screen_size['width'] // 2

                # Controlled scroll
                driver.swipe(center_x, start_y, center_x, end_y, 600)
                time.sleep(1.5)  # Wait for elements to load

                # Verify scroll was effective
                try:
                    post_scroll_elements = driver.find_elements(AppiumBy.XPATH, working_selector)
                    print(f"[SCROLL] After scroll: found {len(post_scroll_elements)} elements")

                    if len(post_scroll_elements) == 0:
                        print("[SCROLL] No elements after scroll - likely reached end")
                        consecutive_empty_scrolls += 2  # Fast exit
                except:
                    pass

            else:
                print(f"[SCROLL] Stopping scroll - consecutive_empty: {consecutive_empty_scrolls}")

            scroll_attempts += 1

        print(f"\n[COMPLETE] Scraping finished!")
        print(f"[STATS] Total chats found: {len(all_chats)}")

        # Count groups vs individuals
        groups = [chat for chat in all_chats if chat['type'] == 'group']
        individuals = [chat for chat in all_chats if chat['type'] == 'individual']

        print(f"[STATS] Groups: {len(groups)}, Individual chats: {len(individuals)}")

        # Print all group chats found
        if groups:
            print(f"\n{'='*60}")
            print(f"[GROUP CHATS] All {len(groups)} Group Chats Found:")
            print(f"{'='*60}")
            for i, chat in enumerate(groups, 1):
                print(f"{i:2d}. {chat['name']} (Position: {chat['position']})")
            print(f"{'='*60}")
        else:
            print(f"\n[GROUP CHATS] No group chats were found.")

        # Also print individuals if any (shouldn't happen after Groups filter)
        if individuals:
            print(f"\n[INDIVIDUAL CHATS] Found {len(individuals)} individual chats:")
            for i, chat in enumerate(individuals, 1):
                print(f"{i:2d}. {chat['name']} (Position: {chat['position']})")

        return all_chats

    except Exception as e:
        print(f"[ERROR] Error scraping chat names: {str(e)}")
        return []

def save_scraped_chats(chats, filename=None):
    """Save scraped chats to a file"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"txt/scraped_chats_{timestamp}.txt"

    try:
        os.makedirs('txt', exist_ok=True)

        with open(filename, 'w', encoding='utf-8') as file:
            file.write(f"# WhatsApp Chat List - Scraped on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            file.write(f"# Total chats: {len(chats)}\n\n")

            # Write all chats with row numbers
            for chat in chats:
                file.write(f"  - Row {chat['position']}: {chat['name']}\n")

            # Write statistics at the end
            groups = [chat for chat in chats if chat['type'] == 'group']
            individuals = [chat for chat in chats if chat['type'] == 'individual']

            file.write(f"\n# STATISTICS\n")
            file.write(f"# Total chats: {len(chats)}\n")
            file.write(f"# Groups: {len(groups)}\n")
            file.write(f"# Individual chats: {len(individuals)}\n")

        print(f"[SAVED] Chat list saved to {filename}")
        print(f"[SAVED] Groups: {len(groups)}, Individuals: {len(individuals)}")

        return filename

    except Exception as e:
        print(f"[ERROR] Failed to save chat list: {str(e)}")
        return None

def main():
    """Main function to scrape WhatsApp chats"""
    global _global_driver

    # Set up signal handlers for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    driver = None

    try:
        print("="*60)
        print("WhatsApp Chat Scraper")
        print("="*60)
        print("* Press Ctrl+C to stop the scraper at any time")
        print("="*60)
        print("Starting WhatsApp chat scraping...")

        driver = setup_driver()
        _global_driver = driver  # Track for cleanup

        # Turn on screen and open WhatsApp
        success = turn_screen_on_and_unlock(driver)
        if success:
            whatsapp_success = open_whatsapp(driver)
            if whatsapp_success:
                print("WhatsApp is now open and ready for scraping!")
                time.sleep(2)  # Wait for WhatsApp to load

                # Scrape all chats
                scraped_chats = scrape_all_chat_names(driver)

                # Save to file
                if scraped_chats:
                    saved_file = save_scraped_chats(scraped_chats)
                    if saved_file:
                        print(f"\n[SUCCESS] Scraped {len(scraped_chats)} chats successfully!")
                        print(f"[OUTPUT] Results saved to: {saved_file}")
                        print("\nYou can now use this file with your messaging script!")
                    else:
                        print("[ERROR] Failed to save results")
                else:
                    print("[ERROR] No chats were scraped")

            else:
                print("[ERROR] Failed to open WhatsApp")
        else:
            print("[ERROR] Failed to unlock device")

    except Exception as e:
        print(f"[ERROR] Scraping failed: {str(e)}")
        print("Make sure:")
        print("1. Appium server is running (appium)")
        print("2. Android device is connected via USB")
        print("3. USB debugging is enabled")
        print("4. Device is detected (adb devices)")
        print("5. WhatsApp is installed on the device")
    finally:
        if driver:
            print("Closing Appium session...")
            try:
                driver.quit()
                print("Session closed successfully")
            except Exception as e:
                print(f"Error closing session: {e}")
        _global_driver = None  # Clear global reference

if __name__ == "__main__":
    main()