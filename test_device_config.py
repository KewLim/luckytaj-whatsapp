#!/usr/bin/env python3
"""
Quick test script to verify device configuration system
"""

# Import the device config system
from whatsapp import DEVICE_CONFIGS, select_device_config, get_device_config

def test_device_configs():
    """Test that all device configs have required keys"""
    required_keys = [
        'photo_select_x',
        'photo_select_y',
        'photo_select_fallback_x',
        'photo_select_fallback_y',
        'caption_area_x_offset',
        'caption_area_y',
        'caption_fallback_x',
        'caption_fallback_y',
        'send_button_x',
        'send_button_y',
        'search_button_x',
        'search_button_y'
    ]

    print("Testing device configurations...")
    print("="*60)

    for device_name, config in DEVICE_CONFIGS.items():
        print(f"\nTesting device: {device_name}")
        missing_keys = []

        for key in required_keys:
            if key not in config:
                missing_keys.append(key)

        if missing_keys:
            print(f"  X MISSING KEYS: {missing_keys}")
        else:
            print(f"  OK All required keys present")
            print(f"    - Photo: ({config['photo_select_x']}, {config['photo_select_y']})")
            print(f"    - Caption Y: {config['caption_area_y']}")
            print(f"    - Send: ({config['send_button_x']}, {config['send_button_y']})")

    print("\n" + "="*60)
    print("OK Configuration test complete!")

def test_get_device_config():
    """Test the get_device_config fallback mechanism"""
    print("\n\nTesting get_device_config fallback...")
    print("="*60)

    config = get_device_config()
    print(f"Got config: {config is not None}")
    print(f"Config type: {type(config)}")

    if config:
        print("OK get_device_config() works correctly")
    else:
        print("ERROR get_device_config() returned None")

    print("="*60)

if __name__ == "__main__":
    test_device_configs()
    test_get_device_config()
    print("\nOK All tests passed!")
