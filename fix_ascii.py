#!/usr/bin/env python3
"""
ASCII Compliance Fixer for CI/CD Pipeline
Removes all non-ASCII characters from source files
"""
import os
import re
import shutil
from datetime import datetime

def create_backup(file_path):
    """Create a backup of the file"""
    backup_path = f"{file_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(file_path, backup_path)
    return backup_path

def fix_ascii_content(content):
    """Replace non-ASCII characters with ASCII equivalents"""
    
    # Common Unicode replacements
    replacements = {
        # Quotes
        '"': '"',  # U+201C LEFT DOUBLE QUOTATION MARK
        '"': '"',  # U+201D RIGHT DOUBLE QUOTATION MARK
        ''''''': "'",  # U+2019 RIGHT SINGLE QUOTATION MARK
        
        # Dashes
        '-': '-',  # U+2013 EN DASH
        '-': '-',  # U+2014 EM DASH
        
        # Bullets and symbols
        '*': '*',  # U+2022 BULLET
        '->': '->',  # U+2192 RIGHTWARDS ARROW
        '<-': '<-',  # U+2190 LEFTWARDS ARROW
        '^': '^',   # U+2191 UPWARDS ARROW
        'v': 'v',   # U+2193 DOWNWARDS ARROW
        
        # Mathematical symbols
        'x': 'x',   # U+00D7 MULTIPLICATION SIGN
        '/': '/',   # U+00F7 DIVISION SIGN
        '~': '~',   # U+2248 ALMOST EQUAL TO
        '!=': '!=',  # U+2260 NOT EQUAL TO
        '<=': '<=',  # U+2264 LESS-THAN OR EQUAL TO
        '>=': '>=',  # U+2265 GREATER-THAN OR EQUAL TO
        
        # Special characters
        '...': '...',  # U+2026 HORIZONTAL ELLIPSIS
        ' degrees': ' degrees',  # U+00B0 DEGREE SIGN
        
        # Common emojis - replace with text descriptions
        '**[ROCKET]**': '**[ROCKET]**',
        '**[CHECK]**': '**[CHECK]**',
        '**[X]**': '**[X]**',
        '**[WARNING]**': '**[WARNING]**',
        '**[ZAP]**': '**[LIGHTNING]**',
        '**[FIRE]**': '**[FIRE]**',
        '**[LIGHT-BULB]**': '**[IDEA]**',
        '**[BAR-CHART]**': '**[CHART]**',
        '**[LINE-CHART]**': '**[TRENDING-UP]**',
        '**[TRENDING-DOWN]**': '**[TRENDING-DOWN]**',
        '**[TARGET]**': '**[TARGET]**',
        '**[WRENCH]**': '**[WRENCH]**',
        '*': '*',
        '**[SPARKLES]**': '**[SPARKLES]**',
        '**[STAR]**': '**[STAR]**',
        '**[COMPUTER]**': '**[COMPUTER]**',
        '**[DESKTOP]**': '**[DESKTOP]**',
        '**[MOBILE]**': '**[MOBILE]**',
        '**[EARTH]**': '**[EARTH]**',
        '**[EARTH]**': '**[EARTH]**',
        '**[EARTH]**': '**[EARTH]**',
        '**[SATELLITE]**': '**[SATELLITE]**',
        '**[SPACE]**': '**[SPACE]**',
        '**[COMET]**': '**[COMET]**',
        '**[SHOOTING-STAR]**': '**[SHOOTING-STAR]**',
        '**[TELESCOPE]**': '**[TELESCOPE]**',
        '**[ALARM]**': '**[ALARM]**',
        '**[CLOCK]**': '**[CLOCK]**',
        '**[CALENDAR]**': '**[CALENDAR]**',
        '**[BAR-CHART]**': '**[BAR-CHART]**',
        '**[LINE-CHART]**': '**[LINE-CHART]**',
        '**[MAGNIFYING-GLASS]**': '**[MAGNIFYING-GLASS]**',
        '**[TEST-TUBE]**': '**[TEST-TUBE]**',
        '**[ALEMBIC]**': '**[ALEMBIC]**',
        '**[MICROSCOPE]**': '**[MICROSCOPE]**',
        '**[SATELLITE-ANTENNA]**': '**[SATELLITE-ANTENNA]**',
        '**[ANTENNA-BARS]**': '**[ANTENNA-BARS]**',
        '**[GEAR]**': '**[GEAR]**',
        '**[NUT-AND-BOLT]**': '**[NUT-AND-BOLT]**',
        '**[HAMMER]**': '**[HAMMER]**',
        '**[TOOLBOX]**': '**[TOOLBOX]**',
        '**[CLIPBOARD]**': '**[CLIPBOARD]**',
        '**[MEMO]**': '**[MEMO]**',
        '**[PAGE]**': '**[PAGE]**',
        '**[PAGE-WITH-CURL]**': '**[PAGE-WITH-CURL]**',
        '**[BOOKMARK-TABS]**': '**[BOOKMARK-TABS]**',
        '**[CARD-INDEX-DIVIDERS]**': '**[CARD-INDEX-DIVIDERS]**',
        '**[FOLDER]**': '**[FOLDER]**',
        '**[OPEN-FOLDER]**': '**[OPEN-FOLDER]**',
        '**[CARD-FILE-BOX]**': '**[CARD-FILE-BOX]**',
        '**[FILE-CABINET]**': '**[FILE-CABINET]**',
        '**[FLOPPY-DISK]**': '**[FLOPPY-DISK]**',
        '**[CD]**': '**[CD]**',
        '**[DVD]**': '**[DVD]**',
        '**[MINIDISC]**': '**[MINIDISC]**',
        '**[ZAP]**': '**[ZAP]**',
        '**[BATTERY]**': '**[BATTERY]**',
        '**[ELECTRIC-PLUG]**': '**[ELECTRIC-PLUG]**',
        '**[LIGHT-BULB]**': '**[LIGHT-BULB]**',
        '**[FLASHLIGHT]**': '**[FLASHLIGHT]**',
        '**[CANDLE]**': '**[CANDLE]**',
        '**[FIRE]**': '**[FIRE]**',
        '**[BOOM]**': '**[BOOM]**',
        '**[ANGER]**': '**[ANGER]**',
        '**[SWEAT-DROPLETS]**': '**[SWEAT-DROPLETS]**',
        '**[DASH]**': '**[DASH]**',
        '**[TORNADO]**': '**[TORNADO]**',
        '**[WATER-WAVE]**': '**[WATER-WAVE]**',
        '**[MOUNTAIN]**': '**[MOUNTAIN]**',
        '**[MOUNT-FUJI]**': '**[MOUNT-FUJI]**',
        '**[VOLCANO]**': '**[VOLCANO]**',
        '**[DESERT]**': '**[DESERT]**',
        '**[BEACH]**': '**[BEACH]**',
        '**[ISLAND]**': '**[ISLAND]**',
        '**[GLOBE]**': '**[GLOBE]**',
        '**[WORLD-MAP]**': '**[WORLD-MAP]**',
        '**[COMPASS]**': '**[COMPASS]**',
        '**[CHECKERED-FLAG]**': '**[CHECKERED-FLAG]**',
        '**[TRIANGULAR-FLAG]**': '**[TRIANGULAR-FLAG]**',
        '**[WHITE-FLAG]**': '**[WHITE-FLAG]**',
        '**[BLACK-FLAG]**': '**[BLACK-FLAG]**',
        '**[FLAG-IN-HOLE]**': '**[FLAG-IN-HOLE]**'
    }
    
    # Apply replacements
    for unicode_char, ascii_replacement in replacements.items():
        content = content.replace(unicode_char, ascii_replacement)
    
    # Remove any remaining non-ASCII characters by replacing with '?'
    # But be more selective - keep newlines, tabs, etc.
    content = re.sub(r'[^\x00-\x7F]', '?', content)
    
    return content

def fix_file_ascii(file_path):
    """Fix ASCII compliance in a single file"""
    try:
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Check if file has non-ASCII characters
        if not re.search(r'[^\x00-\x7F]', original_content):
            return False, "Already ASCII compliant"
        
        # Create backup
        backup_path = create_backup(file_path)
        
        # Fix ASCII issues
        fixed_content = fix_ascii_content(original_content)
        
        # Write back the fixed content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        # Count changes
        original_non_ascii = len(re.findall(r'[^\x00-\x7F]', original_content))
        remaining_non_ascii = len(re.findall(r'[^\x00-\x7F]', fixed_content))
        
        return True, f"Fixed {original_non_ascii} non-ASCII chars (backup: {backup_path})"
        
    except Exception as e:
        return False, f"Error: {e}"

def main():
    """Main function to fix ASCII compliance across all source files"""
    print("ASCII Compliance Fixer")
    print("=" * 50)
    
    # Find all Python, YAML files
    target_extensions = ['.py', '.yml', '.yaml']
    exclude_dirs = {'.venv', 'venv', '__pycache__', '.git', 'node_modules', '.pytest_cache'}
    
    files_to_check = []
    for root, dirs, files in os.walk('.'):
        # Remove excluded directories from dirs to prevent traversal
        dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith('.')]
        
        for file in files:
            if any(file.endswith(ext) for ext in target_extensions):
                file_path = os.path.join(root, file)
                files_to_check.append(file_path)
    
    print(f"Found {len(files_to_check)} files to check")
    print()
    
    fixed_count = 0
    error_count = 0
    
    for file_path in files_to_check:
        print(f"Checking: {file_path}")
        success, message = fix_file_ascii(file_path)
        
        if success:
            fixed_count += 1
            print(f"  ? {message}")
        else:
            if "Already ASCII compliant" in message:
                print(f"  - {message}")
            else:
                error_count += 1
                print(f"  ? {message}")
        print()
    
    print("=" * 50)
    print(f"ASCII Compliance Fix Summary:")
    print(f"  Files checked: {len(files_to_check)}")
    print(f"  Files fixed: {fixed_count}")
    print(f"  Errors: {error_count}")
    
    if error_count == 0:
        print("\n**[CHECK]** All files are now ASCII compliant!")
        print("   CI/CD pipeline should pass now.")
    else:
        print(f"\n**[WARNING]**  {error_count} files had errors and may need manual review.")
    
    return error_count == 0

if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)