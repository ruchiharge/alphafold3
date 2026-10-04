from openmm.app import *
from openmm import *
from openmm.unit import *

# 1. Load the CIF file
cif = PDBxFile('demo6E_model.cif')

# 2. Load the force field
forcefield = ForceField('amber19-all.xml', 'amber19/tip3pfb.xml')

# --- FIX START ---
# 3. Create a Modeller object and add missing hydrogens
modeller = Modeller(cif.topology, cif.positions)
modeller.addHydrogens(forcefield) 

# Now use 'modeller' instead of 'cif' for the topology and positions
system = forcefield.createSystem(modeller.topology, nonbondedMethod=NoCutoff)
# --- FIX END ---

# 4. Set up the Simulation
integrator = LangevinIntegrator(300*kelvin, 1/picosecond, 0.002*picoseconds)
simulation = Simulation(modeller.topology, system, integrator)
simulation.context.setPositions(modeller.positions)

# 5. Get and print the Potential Energy
state = simulation.context.getState(getEnergy=True)
print(f"Potential Energy: {state.getPotentialEnergy()}")