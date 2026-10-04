import csv

file_path = '5T89_VEGF_VEGFR_Complex_ranking_scores.csv'

max_row = None
max_score = -1.0

with open(file_path, mode='r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        # Convert score to float for comparison
        current_score = float(row['ranking_score'])
        
        if current_score > max_score:
            max_score = current_score
            max_row = row

if max_row:
    print(f"seed: {max_row['seed']}")
    print(f"sample: {max_row['sample']}")
    print(f"ranking_score: {max_row['ranking_score']}")