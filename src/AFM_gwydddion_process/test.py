from pathlib import Path

root = Path("./data")  # 改成你的路径

for item in root.iterdir():
    if item.is_dir():
        print(item)