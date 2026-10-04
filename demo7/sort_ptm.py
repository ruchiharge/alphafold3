from pathlib import Path


DEMO7_DIR = Path(__file__).resolve().parent
INPUT_FILE = DEMO7_DIR / "ptm_scores.txt"
OUTPUT_FILE = DEMO7_DIR / "ptm_sorted.txt"


def parse_ptm(row):
    columns = row.rstrip("\n").split("\t")
    if len(columns) < 3:
        raise ValueError(f"Expected at least 3 columns, got {len(columns)}")

    return float(columns[2])


def main():
    with INPUT_FILE.open("r", encoding="utf-8") as file:
        header = file.readline()
        rows = [line for line in file if line.strip()]

    sorted_rows = sorted(rows, key=parse_ptm, reverse=True)

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        file.write(header)
        file.writelines(sorted_rows)


if __name__ == "__main__":
    main()
