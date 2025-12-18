from pathlib import Path
root = Path(r"c:\Users\activ\Desktop\gym_management")
for path in root.rglob("*.html"):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for i, line in enumerate(f, 1):
            if "url" in line and "list" in line:
                print(path, i, line.strip())
