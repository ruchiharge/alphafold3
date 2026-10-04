"""Run ChimeraX H-bond counts for every demo7 model.

Run inside ChimeraX, for example from the ChimeraX command line:

    runscript "C:/Users/Sriva/Desktop/material/4-2 Books/alphafold/demo7/h-bond.py"

The script opens each demo7*/demo7*_model.cif file, runs the ChimeraX
`hbonds` command for each chain pair, and writes a tab-separated summary to
demo7/h-bond-output.txt.
"""

from __future__ import annotations

import re
from pathlib import Path

from chimerax.core.commands import run


DEMO7_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = DEMO7_DIR / "h-bond-output.txt"
TEMP_FILE = DEMO7_DIR / "_hbond_tmp.txt"

# demo7 chain convention:
# A, B = VEGFA(mut); C, D = VEGFR D2/D3.
# Keeping all six pairwise chain combinations makes the output complete.
CHAIN_PAIRS = [
    ("A", "B"),
    ("A", "C"),
    ("A", "D"),
    ("B", "C"),
    ("B", "D"),
    ("C", "D"),
]


def chimera_path(path: Path) -> str:
    """Return a ChimeraX-safe quoted path."""
    return str(path).replace("\\", "/")


def demo7_model_files() -> list[Path]:
    """Find one best-model CIF for every demo7 amino-acid folder."""
    return sorted(
        path
        for folder in DEMO7_DIR.iterdir()
        if folder.is_dir() and re.fullmatch(r"demo7[A-Z]", folder.name)
        for path in folder.glob("*_model.cif")
    )


def parse_hbond_count(save_file: Path) -> int:
    """Extract the count from a ChimeraX hbonds saveFile output."""
    if not save_file.exists():
        return 0

    lines = save_file.read_text(encoding="utf-8", errors="replace").splitlines()

    # ChimeraX commonly writes a summary line such as "11 H-bonds".
    for line in lines:
        match = re.search(r"(\d+)\s+(?:H-bonds|hydrogen bonds?)", line, re.IGNORECASE)
        if match:
            return int(match.group(1))

    # Fallback: count data-looking lines if the exact summary wording differs.
    count = 0
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        lowered = stripped.lower()
        if "donor" in lowered or "acceptor" in lowered or "h-bond" in lowered:
            continue
        if "/" in stripped:
            count += 1
    return count


def count_hbonds(session, chain_a: str, chain_b: str) -> int:
    """Run ChimeraX hbonds for one chain pair and return the number found."""
    if TEMP_FILE.exists():
        TEMP_FILE.unlink()

    command = (
        f'hbonds /{chain_a} restrict /{chain_b} '
        f'showDist true log false reveal false '
        f'saveFile "{chimera_path(TEMP_FILE)}"'
    )
    run(session, command)
    return parse_hbond_count(TEMP_FILE)


def main(session) -> None:
    models = demo7_model_files()
    if not models:
        raise FileNotFoundError(f"No demo7 *_model.cif files found under {DEMO7_DIR}")

    with OUTPUT_FILE.open("w", encoding="utf-8", newline="") as output:
        output.write("structure\tresidue\tchain_pair\th_bonds\n")

        for model_path in models:
            structure = model_path.parent.name
            residue = structure.removeprefix("demo7")

            run(session, "close")
            run(session, f'open "{chimera_path(model_path)}"')

            for chain_a, chain_b in CHAIN_PAIRS:
                pair = f"{chain_a}-{chain_b}"
                try:
                    hbond_count = count_hbonds(session, chain_a, chain_b)
                    output.write(f"{structure}\t{residue}\t{pair}\t{hbond_count}\n")
                except Exception as exc:
                    output.write(
                        f"{structure}\t{residue}\t{pair}\tERROR: "
                        f"{type(exc).__name__}: {exc}\n"
                    )
                output.flush()

        run(session, "close")

    if TEMP_FILE.exists():
        TEMP_FILE.unlink()

    print(f"Wrote H-bond counts to {OUTPUT_FILE}")


main(session)
