#!/usr/bin/env python3
"""
Script to remove emojis and non-ASCII characters from project files
"""

import os
import re
import codecs

def remove_emojis_from_file(file_path):
    """Remove emojis and replace with ASCII equivalents"""
    
    # Emoji replacements
    emoji_replacements = {
        '🚀': '',
        '🧪': '',
        '📥': '',
        '🐍': '',
        '📦': '',
        '🔧': '',
        '🔍': '',
        '🎯': '',
        '🏗️': '',
        '📊': '',
        '📤': '',
        '🌊': '',
        '🔑': '',
        '🌐': '',
        '🔒': '',
        '⚡': '',
        '⏱️': '',
        'ℹ️': '',
        '📋': '',
        '🔵': '',
        '✅': '',
        '⚠️': '',
        '❌': '',
        '🛰️': '',
        '🚨': '',
        '🔄': '',
        '🔍': '',
        '📡': '',
        '🔥': '',
        '🌍': '',
        '📍': '',
        '📅': '',
        '🏔️': '',
        '⚖️': '',
        '🔢': '',
        '💥': '',
        'Δ': 'Delta',
        '°': ' degrees'
    }
    
    try:
        # Read file with UTF-8 encoding
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace emojis and special characters
        modified = False
        for emoji, replacement in emoji_replacements.items():
            if emoji in content:
                content = content.replace(emoji, replacement)
                modified = True
        
        # Remove any remaining non-ASCII characters (except newlines and tabs)
        original_content = content
        content = re.sub(r'[^\x00-\x7F\n\r\t]', '', content)
        
        if content != original_content:
            modified = True
        
        if modified:
            # Write back to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed: {file_path}")
            return True
        else:
            print(f"No changes needed: {file_path}")
            return False
            
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Main function to process all relevant files"""
    project_root = r"c:\Users\Antho\OneDrive\Desktop\Space Debris Risk Assessment"
    
    # Files to process
    files_to_fix = [
        '.github/workflows/ci-cd.yml',
        '.github/workflows/cross-platform.yml', 
        '.github/workflows/release.yml',
        'app_standalone.py'
    ]
    
    fixed_count = 0
    
    for file_path in files_to_fix:
        full_path = os.path.join(project_root, file_path)
        if os.path.exists(full_path):
            if remove_emojis_from_file(full_path):
                fixed_count += 1
        else:
            print(f"File not found: {full_path}")
    
    print(f"\nFixed {fixed_count} files")

if __name__ == "__main__":
    main()