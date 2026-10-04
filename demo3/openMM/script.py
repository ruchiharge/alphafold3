import os
from openmm.app import *
from openmm import *
from openmm.unit import *

# 1. Setup Force Field (Loaded once to save time)
forcefield = ForceField('amber14-all.xml', 'amber14/tip3pfb.xml')

# 2. Open the output file for writing
with open('output.txt', 'w') as f:
    f.write("File Name, Potential Energy (kJ/mol)\n")
    f.write("-" * 40 + "\n")

    # 3. Loop through all files in the current directory
    for filename in os.listdir('.'):
        if filename.endswith('.cif'):
            print(f"Processing {filename}...")
            
            try:
                # Load file
                cif = PDBxFile(filename)
                
                # Add Hydrogens
                modeller = Modeller(cif.topology, cif.positions)
                modeller.addHydrogens(forcefield) 
                
                # Create System
                system = forcefield.createSystem(modeller.topology, nonbondedMethod=NoCutoff)
                
                # Setup Simulation
                integrator = LangevinIntegrator(300*kelvin, 1/picosecond, 0.002*picoseconds)
                simulation = Simulation(modeller.topology, system, integrator)
                simulation.context.setPositions(modeller.positions)
                
                # Get Energy
                state = simulation.context.getState(getEnergy=True)
                energy = state.getPotentialEnergy()
                
                # Write to file
                f.write(f"{filename}, {energy}\n")
                print(f"Done: {energy}")

            except Exception as e:
                error_msg = f"Error processing {filename}: {str(e)}"
                f.write(f"{filename}, ERROR\n")
                print(error_msg)

print("Batch processing complete. Results saved to output.txt.")