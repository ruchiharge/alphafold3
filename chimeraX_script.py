from chimerax.core.commands import run
from chimerax.geometry import distance
import os

# --- SETTINGS ---
CHAIN_1 = "A"
CHAIN_2 = "B"
CUTOFF = 5.0
# Change this path to where you want the file saved
OUTPUT_PATH = os.path.expanduser("~/Desktop/distances_under_5A.txt")

def save_distances(session):
    # 1. Select and get atoms
    atoms1 = run(session, f"select /{CHAIN_1}").atoms
    atoms2 = run(session, f"select /{CHAIN_2}").atoms
    run(session, "select clear")

    if not atoms1 or not atoms2:
        print("Error: One or both chains not found.")
        return

    # 2. Open file for writing
    with open(OUTPUT_PATH, "w") as f:
        f.write(f"Distances < {CUTOFF}A between Chain {CHAIN_1} and Chain {CHAIN_2}\n")
        f.write(f"{'Dist(A)':<10} | {'Res1':<10} | {'Atom1':<6} | {'Res2':<10} | {'Atom2':<6}\n")
        f.write("-" * 55 + "\n")

        count = 0
        for a1 in atoms1:
            for a2 in atoms2:
                d = distance(a1.scene_coord, a2.scene_coord)
                if d <= CUTOFF:
                    line = f"{d:<10.3f} | {a1.residue.name}{a1.residue.number:<5} | {a1.name:<6} | {a2.residue.name}{a2.residue.number:<5} | {a2.name:<6}\n"
                    f.write(line)
                    count += 1
        
    print(f"Finished! Found {count} contacts. Saved to: {OUTPUT_PATH}")

save_distances(session)