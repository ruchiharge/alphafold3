import csv

file_path = 'demo3_3_6BFT_2_VEGFR_D1_D2_2_VEGFA_ranking_scores.csv'

max_row = None
max_score = float('-inf')

min_row = None
min_score = float('inf')

with open(file_path, mode='r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        current_score = float(row['ranking_score'])
        
        # Update maximum
        if current_score > max_score:
            max_score = current_score
            max_row = row
            
        # Update minimum
        if current_score < min_score:
            min_score = current_score
            min_row = row

if max_row:
    print("--- Maximum Score ---")
    print(f"seed: {max_row['seed']}")
    print(f"sample: {max_row['sample']}")
    print(f"ranking_score: {max_row['ranking_score']}")

if min_row:
    print("\n--- Minimum Score ---")
    print(f"seed: {min_row['seed']}")
    print(f"sample: {min_row['sample']}")
    print(f"ranking_score: {min_row['ranking_score']}")