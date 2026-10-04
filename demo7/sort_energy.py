from pathlib import Path


DEMO7_DIR = Path(__file__).resolve().parent
INPUT_FILE = DEMO7_DIR / "output.txt"
OUTPUT_FILE = DEMO7_DIR / "sorted_energy.txt"


def parse_energy(row):
    columns = row.rstrip("\n").split("\t")
    if len(columns) < 2:
        raise ValueError(f"Expected at least 2 columns, got {len(columns)}")

    return float(columns[1])


def main():
    with INPUT_FILE.open("r", encoding="utf-8") as file:
        header = file.readline()
        rows = [line for line in file if line.strip()]

    sorted_rows = sorted(rows, key=parse_energy)

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        file.write(header)
        file.writelines(sorted_rows)


if __name__ == "__main__":
    main()
