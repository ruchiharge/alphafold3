import json
from pathlib import Path


DEMO7_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = DEMO7_DIR / "ptm_scores.txt"


def get_demo_folders():
    return sorted(
        path
        for path in DEMO7_DIR.iterdir()
        if path.is_dir() and path.name.startswith("demo7")
    )


def extract_ptm(summary_file):
    with summary_file.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if "ptm" not in data:
        raise KeyError("ptm")

    return data["ptm"]


def main():
    demo_folders = get_demo_folders()

    with OUTPUT_FILE.open("w", encoding="utf-8") as output:
        output.write("folder\tsummary_confidences_file\tptm\n")

        for demo_folder in demo_folders:
            summary_files = sorted(demo_folder.glob("*_summary_confidences.json"))

            if not summary_files:
                output.write(f"{demo_folder.name}\tERROR\tNo summary confidences JSON found\n")
                continue

            for summary_file in summary_files:
                try:
                    ptm = extract_ptm(summary_file)
                    output.write(f"{demo_folder.name}\t{summary_file.name}\t{ptm}\n")
                except Exception as exc:
                    output.write(
                        f"{demo_folder.name}\t{summary_file.name}\t"
                        f"ERROR: {type(exc).__name__}: {exc}\n"
                    )


if __name__ == "__main__":
    main()
