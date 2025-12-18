from pathlib import Path
import re
root = Path(r"c:\Users\activ\Desktop\gym_management")
pattern = re.compile(r"\{\%\s*url\s+['\"]([^'\"]+)['\"]")
for path in root.rglob("*.html"):
    with path.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            m = pattern.search(line)
            if m:
                name = m.group(1)
                if ':' not in name and name not in ('logout', 'login'):
                    print(path, i, name, line.strip())
