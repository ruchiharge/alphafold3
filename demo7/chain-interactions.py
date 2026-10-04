"""Find close atom-atom interactions between demo7 chains.

Run inside ChimeraX, for example from the ChimeraX command line:

    runscript "C:/Users/Sriva/Desktop/alphafold/demo7/chain-interactions.py"

The script opens each demo7*/demo7*_model.cif file and writes all atom pairs
from different chains that are within 3.0 A of each other.
"""

from __future__ import annotations

import re
from pathlib import Path

from chimerax.core.commands import run
from chimerax.geometry import distance


DEMO7_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = DEMO7_DIR / "chain-interactions-output.txt"
THRESHOLD_ANGSTROM = 3.0

# demo7 chain convention:
# A, B = VEGFA(mut); C, D = VEGFR D2/D3.
# All six different-chain pairs are included.
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


def atom_label(atom, fallback_chain: str) -> tuple[str, str, str]:
    """Return chain, residue label, atom name for output."""
    residue = atom.residue
    chain_id = getattr(residue, "chain_id", "") or fallback_chain
    residue_label = f"{residue.name}{residue.number}"
    return chain_id, residue_label, atom.name


def selected_atoms(session, chain_id: str):
    """Select and return atoms for one chain."""
    selection = run(session, f"select /{chain_id}")
    atoms = selection.atoms
    run(session, "select clear")
    return atoms


def close_interactions(session, chain_a: str, chain_b: str):
    """Return atom pairs within THRESHOLD_ANGSTROM, sorted by distance."""
    atoms_a = selected_atoms(session, chain_a)
    atoms_b = selected_atoms(session, chain_b)

    interactions = []
    for atom_a in atoms_a:
        coord_a = atom_a.scene_coord
        for atom_b in atoms_b:
            dist = distance(coord_a, atom_b.scene_coord)
            if dist <= THRESHOLD_ANGSTROM:
                interactions.append((dist, atom_a, atom_b))

    interactions.sort(key=lambda row: row[0])
    return interactions


def main(session) -> None:
    models = demo7_model_files()
    if not models:
        raise FileNotFoundError(f"No demo7 *_model.cif files found under {DEMO7_DIR}")

    with OUTPUT_FILE.open("w", encoding="utf-8", newline="") as output:
        output.write(
            "structure\tresidue\tchain_pair\tinteraction_count\tdistance_A\t"
            "chain1\tresidue1\tatom1\tchain2\tresidue2\tatom2\n"
        )

        for model_path in models:
            structure = model_path.parent.name
            residue = structure.removeprefix("demo7")

            run(session, "close")
            run(session, f'open "{chimera_path(model_path)}"')

            for chain_a, chain_b in CHAIN_PAIRS:
                pair = f"{chain_a}-{chain_b}"

                try:
                    interactions = close_interactions(session, chain_a, chain_b)
                    interaction_count = len(interactions)

                    if not interactions:
                        output.write(
                            f"{structure}\t{residue}\t{pair}\t0\t\t\t\t\t\t\t\n"
                        )
                        output.flush()
                        continue

                    for dist, atom_a, atom_b in interactions:
                        chain1, residue1, atom1 = atom_label(atom_a, chain_a)
                        chain2, residue2, atom2 = atom_label(atom_b, chain_b)
                        output.write(
                            f"{structure}\t{residue}\t{pair}\t{interaction_count}\t"
                            f"{dist:.3f}\t{chain1}\t{residue1}\t{atom1}\t"
                            f"{chain2}\t{residue2}\t{atom2}\n"
                        )
                except Exception as exc:
                    output.write(
                        f"{structure}\t{residue}\t{pair}\tERROR\t\t"
                        f"{type(exc).__name__}: {exc}\t\t\t\t\t\n"
                    )

                output.flush()

        run(session, "close")

    print(
        f"Wrote chain interactions within {THRESHOLD_ANGSTROM:.1f} A to "
        f"{OUTPUT_FILE}"
    )


main(session)
