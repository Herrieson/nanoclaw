import os
import csv

def build_env():
    # Create directories using relative paths
    os.makedirs('assay_runs', exist_ok=True)
    os.makedirs('deliverables', exist_ok=True)
    os.makedirs('skills/data_round_01_aligned_mix_800_0216', exist_ok=True)

    # Data batch 1 (Glucose and Insulin are replaced by Assay_Hash_Code)
    data1 = [
        ['SubjectID', 'Resting_Heart_Rate', 'Assay_Hash_Code'],
        ['SUBJ_001', '60', 'HASH_001'],    # Will map to G:90, I:10 -> MEQ: 9.0
        ['SUBJ_002', '50', 'HASH_002'],    # Will map to G:100, I:5 -> MEQ: 16.66
        ['SUBJ_003', '70', 'HASH_003'],    # Will map to G:85, I:15 -> MEQ: 6.61
        ['SUBJ_004', '60', 'HASH_004']     # Will map to G:-5, I:10 -> Invalid (negative)
    ]

    # Data batch 2
    data2 = [
        ['SubjectID', 'Resting_Heart_Rate', 'Assay_Hash_Code'],
        ['SUBJ_005', '45', 'HASH_005'],    # Will map to G:110, I:4 -> MEQ: 20.625
        ['SUBJ_006', '55', 'HASH_006'],    # Will map to G:95, I:8 -> MEQ: 10.88
        ['SUBJ_007', '60', 'HASH_007'],    # Will map to G:100, I:null -> Invalid (missing)
        ['SUBJ_008', '-10', 'HASH_008']    # Invalid HR (negative) -> Will map to valid G/I, but HR is invalid
    ]
    
    # Noise data (to test robust parsing)
    data3 = [
        ['Log output from machine XT-9000'],
        ['Error: Calibration failed at 02:00 AM'],
        ['SubjectID', 'Resting_Heart_Rate', 'Assay_Hash_Code'],
        ['SUBJ_009', '80', 'HASH_009'],    # Will map to G:120, I:12 -> MEQ: 13.33
        ['SUBJ_010', '60', 'HASH_010']     # Will map to G:NaN, I:10 -> Invalid
    ]

    with open('assay_runs/batch_A.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(data1)

    with open('assay_runs/batch_B.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(data2)
        
    with open('assay_runs/machine_log_C.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(data3)

if __name__ == '__main__':
    build_env()
