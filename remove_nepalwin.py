"""
Script to remove all instances of "NepalWin🇳🇵" from chat_name.txt
"""

import re

# Read the file
input_file = r"C:\Users\BDC Computer ll\Documents\Appium-test\txt\chat_name.txt"
output_file = r"C:\Users\BDC Computer ll\Documents\Appium-test\txt\chat_name.txt"

with open(input_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Remove all variations of "NepalWin🇳🇵" (with or without spaces)
# This pattern matches "NepalWin" followed by optional spaces and the Nepal flag emoji
cleaned_content = re.sub(r'NepalWin\s*🇳🇵', '', content)

# Write back to the file
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(cleaned_content)

print(f"Successfully removed all NepalWin text instances from {input_file}")
print(f"File has been cleaned and saved.")
