import os
import csv

def build_env():
    # Create directories using relative paths
    os.makedirs('assay_runs', exist_ok=True)
    os.makedirs('deliverables', exist_ok=True)

    # Data batch 1
    data1 = [
        ['SubjectID', 'Fasting_Glucose', 'Insulin', 'Resting_Heart_Rate'],
        ['SUBJ_001', '90', '10', '60'],    # MEQ: (90/10) * (60/60) = 9.0
        ['SUBJ_002', '100', '5', '50'],    # MEQ: (100/5) * (50/60) = 16.66
        ['SUBJ_003', '85', '15', '70'],    # MEQ: (85/15) * (70/60) = 6.61
        ['SUBJ_004', '-5', '10', '60']     # Invalid (negative)
    ]

    # Data batch 2
    data2 = [
        ['SubjectID', 'Fasting_Glucose', 'Insulin', 'Resting_Heart_Rate'],
        ['SUBJ_005', '110', '4', '45'],    # MEQ: (110/4) * (45/60) = 20.625
        ['SUBJ_006', '95', '8', '55'],     # MEQ: (95/8) * (55/60) = 10.88
        ['SUBJ_007', '100', '', '60'],     # Invalid (missing)
        ['SUBJ_008', '90', '10', '-10']    # Invalid (negative)
    ]
    
    # Noise data (to test robust parsing)
    data3 = [
        ['Log output from machine XT-9000'],
        ['Error: Calibration failed at 02:00 AM'],
        ['SubjectID', 'Fasting_Glucose', 'Insulin', 'Resting_Heart_Rate'],
        ['SUBJ_009', '120', '12', '80'],   # MEQ: (120/12) * (80/60) = 13.33
        ['SUBJ_010', 'NaN', '10', '60']    # Invalid
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
