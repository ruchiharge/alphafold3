from Bio.PDB import MMCIFParser, NeighborSearch

# Load the structure
parser = MMCIFParser()
structure = parser.get_structure("AF3_model", "demo3_1_6BFT_complex_model.cif")
model = structure[0]

# Get atom lists for two chains
chain_A_atoms = list(model['A'].get_atoms())
chain_B_atoms = list(model['B'].get_atoms())

# Technique: Use KD-Tree for fast proximity search
ns = NeighborSearch(chain_B_atoms)
# Find all atoms in Chain B within 5.0 Angstroms of any atom in Chain A
close_contacts = ns.search_all(5.0) 

# To find the absolute closest pair:
min_dist = 999.0
closest_pair = None
for atom_a in chain_A_atoms:
    neighbor = ns.search(atom_a.coord, 10.0) # Search within 10A
    for atom_b in neighbor:
        dist = atom_a - atom_b # Euclidean distance
        if dist < min_dist:
            min_dist = dist
            closest_pair = (atom_a, atom_b)

print(f"Closest distance: {min_dist:.2f} Å between {closest_pair[0]} and {closest_pair[1]}")