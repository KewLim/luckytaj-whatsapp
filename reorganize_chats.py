"""
Script to reorganize chat_name.txt based on customer priority list
"""

def normalize_name(name):
    """Normalize names for comparison by removing spaces and converting to lowercase"""
    return name.strip().lower().replace(" ", "")

def reorganize_chats(priority_file, chat_file, output_file):
    """
    Reorganize chat names based on priority list

    Args:
        priority_file: File containing priority customer list (one name per line)
        chat_file: File containing current chat names with NepalWin prefix
        output_file: Output file for reorganized list
    """
    # Read priority list
    with open(priority_file, 'r', encoding='utf-8') as f:
        priority_names = [line.strip() for line in f if line.strip()]

    # Read current chat list
    with open(chat_file, 'r', encoding='utf-8') as f:
        chat_entries = [line.strip() for line in f if line.strip()]

    # Extract names from chat entries (remove NepalWin prefix)
    chat_dict = {}
    for entry in chat_entries:
        if entry.startswith('NepalWin'):
            # Remove various NepalWin prefix formats
            name = entry.replace('NepalWin🇳🇵', '').replace('NepalWin 🇳🇵', '').replace('Nepalwin Api ', '')
            chat_dict[normalize_name(name)] = entry

    # Create reorganized list
    reorganized = []
    matched_names = set()
    unmatched_priority = []

    # Add entries in priority order
    for priority_name in priority_names:
        normalized = normalize_name(priority_name)
        if normalized in chat_dict:
            reorganized.append(chat_dict[normalized])
            matched_names.add(normalized)
        else:
            unmatched_priority.append(priority_name)

    # Add unmatched entries from original chat list at the end
    unmatched_chats = []
    for normalized, entry in chat_dict.items():
        if normalized not in matched_names:
            unmatched_chats.append(entry)

    # Combine all
    final_list = reorganized + unmatched_chats

    # Write to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        for entry in final_list:
            f.write(entry + '\n')

    # Report results
    print(f"[OK] Total priority customers: {len(priority_names)}")
    print(f"[OK] Matched and sorted: {len(reorganized)}")
    print(f"[OK] Not found in chat_name.txt: {len(unmatched_priority)}")
    print(f"[OK] Chat entries not in priority list: {len(unmatched_chats)}")
    print(f"[OK] Total entries in new file: {len(final_list)}")

    if unmatched_priority:
        print(f"\n[WARNING] Customers not found in chat_name.txt ({len(unmatched_priority)}):")
        for name in unmatched_priority[:20]:  # Show first 20
            print(f"  - {name}")
        if len(unmatched_priority) > 20:
            print(f"  ... and {len(unmatched_priority) - 20} more")

    print(f"\n[OK] Reorganized file saved to: {output_file}")

if __name__ == "__main__":
    priority_file = "txt/priority_customers.txt"
    chat_file = "txt/chat_name.txt"
    output_file = "txt/chat_name_reorganized.txt"

    reorganize_chats(priority_file, chat_file, output_file)
