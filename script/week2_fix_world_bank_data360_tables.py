from pathlib import Path

folder = Path("data/external/economy_factor_data")

for file in folder.glob("*.csv"):
    print("=" * 80)
    print(file.name)
    print("=" * 80)

    with open(file, "r", encoding="utf-8", errors="ignore") as f:
        for i in range(10):
            line = f.readline()
            print(f"{i}: {line[:300]}")
        print()