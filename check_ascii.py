#!/usr/bin/env python3
import re
import os

# Define the pattern for non-ASCII characters
pattern = r'[^\x00-\x7F]'

# Files to check
files_to_check = []
for root, dirs, files in os.walk('.'):
    # Skip virtual environment and git directories
    if any(skip in root for skip in ['.venv', 'venv', '__pycache__', '.git']):
        continue
    for file in files:
        if file.endswith(('.py', '.yml', '.yaml')):
            files_to_check.append(os.path.join(root, file))

print(f'Checking {len(files_to_check)} files...')

found_non_ascii = False
for file_path in files_to_check:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if re.search(pattern, content):
            found_non_ascii = True
            print(f'Non-ASCII found in: {file_path}')
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    matches = re.finditer(pattern, line)
                    for match in matches:
                        char = match.group()
                        print(f'  Line {i}: Non-ASCII char "{char}" (U+{ord(char):04X}) at position {match.start()}')
                        print(f'    Context: {line[:max(0, match.start()-10)]}[{char}]{line[match.end():match.end()+10]}')
    except Exception as e:
        print(f'Error reading {file_path}: {e}')

if not found_non_ascii:
    print('SUCCESS: No non-ASCII characters found - CI/CD will pass!')
else:
    print('ERROR: Non-ASCII characters found - CI/CD will fail!')