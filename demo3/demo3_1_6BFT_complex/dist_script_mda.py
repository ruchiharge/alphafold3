import MDAnalysis as mda
from MDAnalysis.analysis import distances

u = mda.Universe("demo3_1_6BFT_complex_model.cif")
chain_A = u.select_atoms("chainID A")
chain_B = u.select_atoms("chainID B")

# Calculate all-to-all distance matrix
dist_matrix = distances.distance_array(chain_A.positions, chain_B.positions)
min_dist = dist_matrix.min()
print(f"Shortest distance between Chain A and B: {min_dist:.2f} Å")