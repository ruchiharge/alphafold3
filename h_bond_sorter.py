def sort_h_bonds_in_place(file_path):
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()

        bond_data = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            parts = line.split()
            
            # Based on your input: "/A LYS 26 NZ /C GLU 9 OE1 no hydrogen 2.692 N/A"
            # Distance (2.692) is the 2nd to last element
            try:
                # We look for the numerical value usually found at index -2
                # If N/A isn't always there, we look for the first float from the right
                distance = None
                for part in reversed(parts):
                    try:
                        distance = float(part)
                        break
                    except ValueError:
                        continue
                
                if distance is not None:
                    bond_data.append((line, distance))
            except (ValueError, IndexError):
                # This handles header lines or malformed lines
                continue

        # Sort by distance (ascending)
        bond_data.sort(key=lambda x: x[1])

        # Overwrite the file with sorted content
        with open(file_path, 'w') as f:
            for original_line, _ in bond_data:
                f.write(original_line + '\n')
        
        print(f"Successfully sorted bonds by distance in '{file_path}'.")

    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")

if __name__ == "__main__":
    sort_h_bonds_in_place('input_h_bond.txt')