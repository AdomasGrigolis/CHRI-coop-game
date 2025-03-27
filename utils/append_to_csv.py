import os
import csv

def append_to_csv(value, filename="times.csv"):
    workspace_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    data_dir = os.path.join(workspace_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    
    # Full path to the CSV file
    file_path = os.path.join(data_dir, filename)
    
    with open(file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([value])

    print(f"Appended value {value} to {file_path}")

if __name__ == "__main__":
    # Test
    append_to_csv(0.0)