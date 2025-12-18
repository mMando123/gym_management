from pathlib import Path
root = Path(r"c:\Users\activ\Desktop\gym_management")
pattern = "{% url"
for path in root.rglob("*.html"):
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            if pattern in line and "'list'" in line:
                print(path, i, line.strip())
            if pattern in line and '"list"' in line:
                print(path, i, line.strip())
