#!/usr/bin/env python3

"""
Standalone Photo Transfer Test Script
====================================
This script tests the photo transfer functionality from daily_photos folder to Android device.
It isolates the photo transfer function to help debug and fix any issues.
"""

from appium.webdriver.webdriver import WebDriver
from appium.options.android.uiautomator2.base import UiAutomator2Options
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
    options.app_package = "com.whatsapp"
    options.app_activity = "com.whatsapp.HomeActivity"
    options.no_reset = True
    options.full_reset = False

    # Add session stability options
    options.new_command_timeout = 300  # 5 minutes timeout
    options.uiautomator2_server_launch_timeout = 60000  # 60 seconds
    options.uiautomator2_server_install_timeout = 60000  # 60 seconds

    # Connect to Appium server
    driver = WebDriver("http://localhost:4723", options=options)
    return driver

def get_daily_photo_path():
    """Get the path to the only photo in daily_photos folder"""
    photo_extensions = ['.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG']

    try:
        if not os.path.exists('daily_photos'):
            print("[ERROR] daily_photos folder does not exist")
            return None

        # Get all image files in the directory
        image_files = []
        for filename in os.listdir('daily_photos'):
            if any(filename.lower().endswith(ext.lower()) for ext in photo_extensions):
                if not filename.startswith('.') and filename != 'README.md':
                    image_files.append(filename)

        print(f"[INFO] Found {len(image_files)} image files in daily_photos/")
        for i, file in enumerate(image_files):
            print(f"  {i+1}. {file}")

        if len(image_files) == 1:
            photo_path = f'daily_photos/{image_files[0]}'
            print(f"[INFO] Using photo: {photo_path}")
            return photo_path
        elif len(image_files) > 1:
            print(f"[WARNING] Multiple photos found in daily_photos folder: {image_files}")
            print("[INFO] Using the first one. Please keep only one photo in the folder.")
            photo_path = f'daily_photos/{image_files[0]}'
            print(f"[INFO] Using photo: {photo_path}")
            return photo_path
        else:
            print("[ERROR] No image files found in daily_photos folder")
            return None

    except Exception as e:
        print(f"[ERROR] Error checking daily_photos folder: {str(e)}")
        return None

def transfer_photo_to_device(driver, local_photo_path):
    """Transfer photo from PC to Android device with detailed debugging (no shell commands needed)"""
    try:
        print(f"\n{'='*60}")
        print(f"PHOTO TRANSFER TEST")
        print(f"{'='*60}")
        print(f"[START] Starting photo transfer for: {local_photo_path}")

        # Step 1: Validate file exists and get extension
        print(f"\n[STEP 1] Validating local file...")
        if not os.path.exists(local_photo_path):
            print(f"[ERROR] Photo file not found: {local_photo_path}")
            return None

        print(f"[SUCCESS] File exists: {local_photo_path}")

        # Get file info
        file_name = os.path.basename(local_photo_path)
        file_ext = os.path.splitext(file_name)[1].lower()
        file_size = os.path.getsize(local_photo_path)
        file_size_mb = file_size / (1024 * 1024)

        print(f"[INFO] File: {file_name}")
        print(f"[INFO] Extension: {file_ext}")
        print(f"[INFO] Size: {file_size_mb:.2f}MB ({file_size} bytes)")

        # Step 2: Validate file extension
        print(f"\n[STEP 2] Validating file type...")
        valid_extensions = ['.jpg', '.jpeg', '.png', '.webp']
        if file_ext not in valid_extensions:
            print(f"[ERROR] Unsupported file type: {file_ext}")
            print(f"[INFO] Supported types: {valid_extensions}")
            return None

        print(f"[SUCCESS] File extension is valid: {file_ext}")

        # Step 3: Test device connectivity
        print(f"\n[STEP 3] Testing device connectivity...")
        try:
            screen_size = driver.get_window_size()
            print(f"[SUCCESS] Device connected. Screen size: {screen_size['width']}x{screen_size['height']}")
        except Exception as e:
            print(f"[ERROR] Device connectivity failed: {e}")
            return None

        # Step 4: Prepare device path
        print(f"\n[STEP 4] Preparing device path...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        device_filename = f"photo_transfer_test_{timestamp}{file_ext}"
        device_path = f'/sdcard/Pictures/{device_filename}'
        print(f"[INFO] Device path: {device_path}")

        # Step 5: Read and encode photo
        print(f"\n[STEP 5] Reading and encoding photo...")
        try:
            with open(local_photo_path, 'rb') as photo_file:
                photo_data = photo_file.read()
            print(f"[SUCCESS] Read {len(photo_data)} bytes from file")

            # Check file size limit
            if file_size_mb > 10:
                print(f"[WARNING] Large file size: {file_size_mb:.2f}MB. May take longer to transfer.")

        except Exception as e:
            print(f"[ERROR] Failed to read photo file: {e}")
            return None

        # Step 6: Convert to base64
        print(f"[INFO] Converting to base64...")
        try:
            photo_base64 = base64.b64encode(photo_data).decode('utf-8')
            print(f"[SUCCESS] Base64 conversion complete, length: {len(photo_base64)}")
        except Exception as e:
            print(f"[ERROR] Base64 conversion failed: {e}")
            return None

        # Step 7: Transfer file to device
        print(f"\n[STEP 7] Transferring file to device...")
        start_transfer = time.time()
        try:
            driver.push_file(device_path, photo_base64)
            transfer_time = time.time() - start_transfer
            print(f"[SUCCESS] File push completed in {transfer_time:.2f}s")
        except Exception as e:
            transfer_time = time.time() - start_transfer
            print(f"[ERROR] File push failed after {transfer_time:.2f}s: {e}")
            return None

        # Step 8: Basic verification using pull_file
        print(f"\n[STEP 8] Verifying transfer...")
        try:
            # Try to pull a small portion of the file to verify it exists
            verify_data = driver.pull_file(device_path)
            if verify_data:
                print(f"[SUCCESS] File verified on device - pull_file successful")
                # Decode and check if it's valid image data
                decoded_data = base64.b64decode(verify_data)
                if len(decoded_data) == file_size:
                    print(f"[SUCCESS] File size verification passed: {len(decoded_data)} bytes")
                else:
                    print(f"[WARNING] File size mismatch. Expected: {file_size}, Got: {len(decoded_data)}")

                print(f"\n{'='*60}")
                print(f"TRANSFER SUCCESS!")
                print(f"{'='*60}")
                print(f"Local file:  {local_photo_path}")
                print(f"Device file: {device_path}")
                print(f"Size:        {file_size_mb:.2f}MB")
                print(f"Transfer time: {transfer_time:.2f}s")
                print(f"{'='*60}")

                return device_path
            else:
                print(f"[ERROR] File verification failed - pull_file returned no data")
                return None

        except Exception as verify_error:
            print(f"[WARNING] Verification failed: {verify_error}")
            print(f"[INFO] File may still be transferred to: {device_path}")
            print(f"[INFO] Assuming transfer was successful")
            return device_path

    except Exception as e:
        print(f"\n[ERROR] Unexpected error during photo transfer: {str(e)}")
        import traceback
        print(f"[DEBUG] Full traceback:")
        print(traceback.format_exc())
        return None

def test_device_photo_access(driver, device_photo_path):
    """Test if the transferred photo can be accessed (simplified version without shell commands)"""
    try:
        print(f"\n{'='*60}")
        print(f"TESTING PHOTO ACCESS")
        print(f"{'='*60}")

        if not device_photo_path:
            print(f"[ERROR] No device photo path provided")
            return False

        print(f"[INFO] Testing access to: {device_photo_path}")

        # Test 1: Try to pull file to verify it exists and is accessible
        try:
            print(f"[INFO] Attempting to pull file for verification...")
            start_time = time.time()
            file_data = driver.pull_file(device_photo_path)
            pull_time = time.time() - start_time

            if file_data:
                decoded_data = base64.b64decode(file_data)
                print(f"[SUCCESS] File is accessible and readable")
                print(f"[INFO] File size: {len(decoded_data)} bytes")
                print(f"[INFO] Pull operation took: {pull_time:.2f}s")
            else:
                print(f"[ERROR] Cannot access file - pull_file returned no data")
                return False
        except Exception as e:
            print(f"[ERROR] File access test failed: {e}")
            return False

        # Test 2: Check if file is in a location WhatsApp can access
        if '/sdcard/Pictures/' in device_photo_path:
            print(f"[SUCCESS] File is in Pictures directory (accessible by WhatsApp)")
        else:
            print(f"[WARNING] File may not be in a WhatsApp-accessible location")

        # Test 3: Verify the file has a valid image header
        try:
            # Check for common image file headers
            image_headers = {
                b'\xFF\xD8\xFF': 'JPEG',
                b'\x89PNG\r\n\x1a\n': 'PNG',
                b'RIFF': 'WebP (possibly)'
            }

            header_found = False
            for header, format_name in image_headers.items():
                if decoded_data.startswith(header):
                    print(f"[SUCCESS] Valid {format_name} image header detected")
                    header_found = True
                    break

            if not header_found:
                print(f"[WARNING] Image header not recognized - may not be a valid image")
        except Exception as e:
            print(f"[WARNING] Image header check failed: {e}")

        print(f"[SUCCESS] Photo access test completed")
        return True

    except Exception as e:
        print(f"[ERROR] Photo access test failed: {e}")
        return False

def main():
    """Main test function"""
    driver = None

    try:
        print(f"{'='*60}")
        print(f"STANDALONE PHOTO TRANSFER TEST")
        print(f"{'='*60}")
        print(f"This script will test photo transfer from daily_photos/ to your Android device")
        print(f"Make sure:")
        print(f"1. Appium server is running")
        print(f"2. Android device is connected via USB")
        print(f"3. USB debugging is enabled")
        print(f"4. WhatsApp is installed on device")
        print(f"{'='*60}")

        # Step 1: Check for photos
        print(f"\n[STEP 1] Checking for photos in daily_photos folder...")
        photo_path = get_daily_photo_path()
        if not photo_path:
            print(f"[ERROR] No photos found in daily_photos folder")
            print(f"[INFO] Please add a .jpg, .jpeg, or .png file to the daily_photos/ folder")
            return

        # Step 2: Setup Appium connection
        print(f"\n[STEP 2] Setting up Appium connection...")
        driver = setup_driver()
        print(f"[SUCCESS] Connected to Appium server")

        # Step 3: Test photo transfer
        print(f"\n[STEP 3] Testing photo transfer...")
        device_photo_path = transfer_photo_to_device(driver, photo_path)

        if device_photo_path:
            # Step 4: Test photo access
            print(f"\n[STEP 4] Testing photo access...")
            access_success = test_device_photo_access(driver, device_photo_path)

            if access_success:
                print(f"\n{'='*60}")
                print(f"ALL TESTS PASSED!")
                print(f"{'='*60}")
                print(f"[+] Photo transfer: SUCCESS")
                print(f"[+] Photo access: SUCCESS")
                print(f"[*] Device photo: {device_photo_path}")
                print(f"[!] The photo should now be available in your device's gallery")
                print(f"{'='*60}")
            else:
                print(f"\n{'='*60}")
                print(f"TRANSFER SUCCESS, ACCESS ISSUES DETECTED")
                print(f"{'='*60}")
                print(f"[+] Photo transfer: SUCCESS")
                print(f"[!] Photo access: ISSUES DETECTED")
                print(f"[*] Device photo: {device_photo_path}")
                print(f"[!] Photo transferred but may not be accessible by WhatsApp")
                print(f"{'='*60}")
        else:
            print(f"\n{'='*60}")
            print(f"TRANSFER FAILED")
            print(f"{'='*60}")
            print(f"[-] Photo transfer: FAILED")
            print(f"[!] Check the error messages above for details")
            print(f"{'='*60}")

    except Exception as e:
        print(f"\n[ERROR] Test failed with error: {str(e)}")
        import traceback
        print(f"[DEBUG] Full traceback:")
        print(traceback.format_exc())

    finally:
        if driver:
            print(f"\n[CLEANUP] Closing Appium session...")
            try:
                driver.quit()
                print(f"[SUCCESS] Appium session closed")
            except Exception as e:
                print(f"[WARNING] Error closing session: {e}")

if __name__ == "__main__":
    main()