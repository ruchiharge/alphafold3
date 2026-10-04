from pathlib import Path

from openmm import LangevinIntegrator
from openmm.app import ForceField, Modeller, NoCutoff, PDBxFile, Simulation
from openmm.unit import kelvin, kilojoule_per_mole, picosecond, picoseconds


DEMO6_DIR = Path(__file__).resolve().parent
BASE_DIR = DEMO6_DIR.parent
OUTPUT_FILE = DEMO6_DIR / "output.txt"


def calculate_potential_energy(cif_path, forcefield):
    cif = PDBxFile(str(cif_path))

    modeller = Modeller(cif.topology, cif.positions)
    modeller.addHydrogens(forcefield)

    system = forcefield.createSystem(modeller.topology, nonbondedMethod=NoCutoff)
    integrator = LangevinIntegrator(300 * kelvin, 1 / picosecond, 0.002 * picoseconds)
    simulation = Simulation(modeller.topology, system, integrator)
    simulation.context.setPositions(modeller.positions)

    state = simulation.context.getState(getEnergy=True)
    energy = state.getPotentialEnergy()
    return energy.value_in_unit(kilojoule_per_mole), energy


def main():
    cif_files = sorted(
        cif_path
        for demo_dir in DEMO6_DIR.iterdir()
        if demo_dir.is_dir() and demo_dir.name.startswith("demo6")
        for cif_path in demo_dir.glob("*.cif")
    )

    if not cif_files:
        raise FileNotFoundError(f"No CIF files found in {DEMO6_DIR}")

    forcefield = ForceField("amber19-all.xml", "amber19/tip3pfb.xml")

    with OUTPUT_FILE.open("w", encoding="utf-8") as output:
        output.write("file\tpotential_energy_kJ_per_mol\tpotential_energy\n")

        for index, cif_path in enumerate(cif_files, start=1):
            relative_path = cif_path.relative_to(BASE_DIR)
            print(f"[{index}/{len(cif_files)}] Processing {relative_path}")

            try:
                energy_kj_per_mol, energy = calculate_potential_energy(cif_path, forcefield)
                output.write(f"{relative_path}\t{energy_kj_per_mol}\t{energy}\n")
            except Exception as exc:
                output.write(f"{relative_path}\tERROR\t{type(exc).__name__}: {exc}\n")

            output.flush()


if __name__ == "__main__":
    main()
