# Device Configuration Guide

This guide explains how to add custom device configurations for different Android devices with varying screen sizes and resolutions.

## Overview

The WhatsApp automation script now supports multiple device configurations. Each device can have its own set of coordinates for tapping photos, captions, send buttons, and search buttons.

## How It Works

1. At script startup, you'll be prompted to select a device configuration
2. The script will use the device-specific coordinates throughout the automation
3. If no device is selected, the script automatically uses the "default" configuration

## Adding a New Device Configuration

### Step 1: Find Your Device's Coordinates

You need to determine the correct tap coordinates for your device. Here's how:

1. **Enable Developer Options** on your Android device:
   - Go to Settings > About Phone
   - Tap "Build Number" 7 times
   - Go back to Settings > Developer Options
   - Enable "Pointer Location" or "Show Taps"

2. **Open WhatsApp** and manually test these coordinates by taking a screenshot with coordinates visible:
   - Photo selection position (first photo in gallery)
   - Caption input area (bottom text field after selecting photo)
   - Send button (green circle with arrow)
   - Search button (magnifying glass icon)

### Step 2: Edit whatsapp.py

Open `whatsapp.py` and find the `DEVICE_CONFIGS` dictionary (around line 22).

Add your device configuration using this template:

```python
DEVICE_CONFIGS = {
    "default": {
        # ... existing default config ...
    },

    # Add your new device here:
    "Your Device Name": {
        "photo_select_x": 180,              # X coordinate for first photo in gallery
        "photo_select_y": 1350,             # Y coordinate for first photo in gallery
        "photo_select_fallback_x": 180,     # Fallback X if primary fails
        "photo_select_fallback_y": 400,     # Fallback Y if primary fails
        "caption_area_x_offset": 0,         # Offset from screen center (usually 0)
        "caption_area_y": 2330,             # Y coordinate for caption input
        "caption_fallback_x": 360,          # Fallback X for caption
        "caption_fallback_y": 1400,         # Fallback Y for caption
        "send_button_x": 990,               # X coordinate for send button
        "send_button_y": 2310,              # Y coordinate for send button
        "search_button_x": 525,             # X coordinate for search icon
        "search_button_y": 330              # Y coordinate for search icon
    }
}
```

### Step 3: Test Your Configuration

1. Run the test script to verify all required keys are present:
   ```bash
   python test_device_config.py
   ```

2. Run the main script and select your device:
   ```bash
   python whatsapp.py
   ```

3. When prompted, enter the number corresponding to your device

## Configuration Parameters Explained

| Parameter | Description | How to Find |
|-----------|-------------|-------------|
| `photo_select_x` | X coordinate of first photo in gallery | Open WhatsApp > Attachment > Gallery, note position of first photo |
| `photo_select_y` | Y coordinate of first photo in gallery | Same as above |
| `photo_select_fallback_x` | Alternative X if first attempt fails | Try a position slightly lower/higher |
| `photo_select_fallback_y` | Alternative Y if first attempt fails | Same as above |
| `caption_area_x_offset` | Horizontal offset from center | Usually 0 (uses screen center) |
| `caption_area_y` | Y coordinate of caption input field | After selecting photo, note text input position |
| `caption_fallback_x` | Alternative caption X position | Middle of screen width |
| `caption_fallback_y` | Alternative caption Y position | Try different Y position |
| `send_button_x` | X coordinate of send button | Note the green send arrow position |
| `send_button_y` | Y coordinate of send button | Same as above |
| `search_button_x` | X coordinate of search icon | Main chat list, top-right corner |
| `search_button_y` | Y coordinate of search icon | Same as above |

## Common Device Resolutions

Here are typical screen sizes for reference:

- **1080x1920 (Full HD)**: Most common Android phones
- **1440x2560 (Quad HD)**: High-end phones
- **720x1280 (HD)**: Budget phones
- **1080x2340 (19.5:9)**: Modern phones with notch

## Tips for Finding Coordinates

1. **Use ADB to Get Screen Size**:
   ```bash
   adb shell wm size
   ```

2. **Take Screenshots with Coordinates**:
   - Enable "Pointer Location" in Developer Options
   - Take screenshots while tapping each location
   - Note the X,Y coordinates shown

3. **Use Appium Inspector**:
   - Install Appium Inspector
   - Connect to your device
   - Use it to inspect element positions

4. **Test Incrementally**:
   - Add your device config
   - Test photo selection first
   - Then test caption, send, and search one by one

## Example Configurations

### Samsung Galaxy S21 (Example)
```python
"Samsung Galaxy S21": {
    "photo_select_x": 200,
    "photo_select_y": 1400,
    "photo_select_fallback_x": 200,
    "photo_select_fallback_y": 450,
    "caption_area_x_offset": 0,
    "caption_area_y": 2400,
    "caption_fallback_x": 380,
    "caption_fallback_y": 1450,
    "send_button_x": 1000,
    "send_button_y": 2380,
    "search_button_x": 540,
    "search_button_y": 340
}
```

### Xiaomi Redmi Note (Example)
```python
"Xiaomi Redmi Note": {
    "photo_select_x": 160,
    "photo_select_y": 1200,
    "photo_select_fallback_x": 160,
    "photo_select_fallback_y": 380,
    "caption_area_x_offset": 0,
    "caption_area_y": 2200,
    "caption_fallback_x": 340,
    "caption_fallback_y": 1320,
    "send_button_x": 940,
    "send_button_y": 2180,
    "search_button_x": 500,
    "search_button_y": 310
}
```

## Troubleshooting

### Photo Not Selected
- The coordinates might be off. Try adjusting `photo_select_y` by ±50 pixels
- Make sure you're testing with actual photos in your gallery

### Caption Area Not Focused
- Try adjusting `caption_area_y` to be closer to the bottom of the screen
- Ensure `caption_area_x_offset` is 0 (center of screen)

### Send Button Not Working
- The send button coordinates can vary. Use Appium Inspector to find exact position
- Try the bottom-right area of the screen

### Search Not Activating
- Search button is usually in the top-right corner
- Try coordinates around (500-600, 300-400) range

## Need Help?

If you're having trouble finding the right coordinates:

1. Run the script with default config and watch the debug output
2. Note which taps succeed/fail
3. Adjust coordinates based on the debug logs
4. Test one coordinate at a time

## Safety Note

Always test your configuration with a small number of chats first (using the range selection feature) to ensure everything works correctly before processing your full chat list.
