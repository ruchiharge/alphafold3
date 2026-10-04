import os
import json
import glob

# Search for all summary_confidences.json files in subdirectories
# Based on your image: seed-X_sample-Y/demo3_1_6BFT_complex_seed-X_sample-Y_summary_confidences.json
file_pattern = os.path.join("seed-*", "*_summary_confidences.json")
summary_files = glob.glob(file_pattern)

interaction_results = []

for file_path in summary_files:
    try:
        # Extract folder name (e.g., seed-4_sample-4) for identification
        folder_name = os.path.dirname(file_path)
        
        with open(file_path, 'r') as f:
            data = json.load(f)
            
        if 'chain_pair_iptm' in data:
            matrix = data['chain_pair_iptm']
            n = len(matrix)
            
            # Sum all off-diagonal elements (where chain i != chain j)
            off_diag_values = [matrix[i][j] for i in range(n) for j in range(n) if i != j]
            
            if off_diag_values:
                avg_interaction = sum(off_diag_values) / len(off_diag_values)
                
                interaction_results.append({
                    'sample': folder_name,
                    'avg_inter_chain_iptm': avg_interaction,
                    'global_iptm': data.get('iptm')
                })
                
    except (json.JSONDecodeError, IOError, KeyError) as e:
        print(f"Skipping {file_path} due to error: {e}")

# Sort by average interaction value in descending order
top_5 = sorted(interaction_results, key=lambda x: x['avg_inter_chain_iptm'], reverse=True)[:5]

# Output the results
print(f"{'Rank':<5} | {'Seed-Sample Folder':<20} | {'Avg Inter-Chain ipTM':<22} | {'Global ipTM'}")
print("-" * 65)
for i, res in enumerate(top_5, 1):
    print(f"{i:<5} | {res['sample']:<20} | {res['avg_inter_chain_iptm']:<22.4f} | {res['global_iptm']}")