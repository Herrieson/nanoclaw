import os
import csv

def build_env():
    os.makedirs('raw_data', exist_ok=True)
    os.makedirs('deliverables', exist_ok=True)

    # Sticky note with thresholds
    with open('raw_data/sticky_note.txt', 'w') as f:
        f.write("Note to self: Valid Relative Fluorescence Units (RFU) for the metabolic in vivo study should be strictly between 0 and 800. Anything outside this range is an amplification artifact! - Dr. Levin\n")

    # Batch A
    with open('raw_data/batch_A.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['sample_id', 'rfu_value'])
        writer.writerow(['S001', '150.5'])
        writer.writerow(['S002', '250.0'])
        writer.writerow(['S003', '-40.2']) # Artifact (negative)

    # Batch B
    with open('raw_data/batch_B.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['sample_id', 'rfu_value'])
        writer.writerow(['S004', '950.0']) # Artifact (over 800)
        writer.writerow(['S005', '300.5'])
        writer.writerow(['S006', '500.0'])
        writer.writerow(['S007', '801.0']) # Artifact (over 800)

if __name__ == "__main__":
    build_env()
