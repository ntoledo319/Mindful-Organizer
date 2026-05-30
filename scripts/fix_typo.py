import os
from pathlib import Path

def replace_in_file(path):
    try:
        content = path.read_text('utf-8')
        if '.mindful_optimizer' in content:
            new_content = content.replace('.mindful_optimizer', '.mindful_organizer')
            path.write_text(new_content, 'utf-8')
            print(f'Updated {path}')
    except Exception as e:
        print(f"Error {path}: {e}")

for root, dirs, files in os.walk('.'):
    if '.git' in root or 'venv' in root or '.venv' in root or '.ruff_cache' in root:
        continue
    for file in files:
        if file.endswith('.py') or file.endswith('.md'):
            replace_in_file(Path(root) / file)
