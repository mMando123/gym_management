from pathlib import Path
import re

ROOT = Path(r"c:\Users\activ\Desktop\gym_management\templates")

# Captures the first token after "url" inside a template tag.
# Examples:
#   {% url 'members:list' %}   -> token="'members:list'"
#   {% url members_list_name %} -> token="members_list_name"
first_token = re.compile(r"\{%\s*url\s+([^\s%]+)")

for path in ROOT.rglob('*.html'):
    text = path.read_text(encoding='utf-8', errors='ignore')
    for i, line in enumerate(text.splitlines(), 1):
        if '{% url' not in line:
            continue
        m = first_token.search(line)
        if not m:
            continue
        token = m.group(1)

        # Skip quoted literals (normal usage)
        if token.startswith("'") or token.startswith('"'):
            continue

        # If it’s unquoted, it’s a variable-driven reverse.
        print(f"{path}:{i}: {line.strip()}")
