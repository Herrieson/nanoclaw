import os
import csv

def build_env():
    # Define directories
    manifests_dir = "manifests"
    os.makedirs(manifests_dir, exist_ok=True)
    
    # Data definitions
    # Fields: Package_ID, Weight_lbs, ZipCode, Recipient
    # Rules for problems: Weight_lbs > 50.0 OR ZipCode is not exactly 5 digits.
    data_file_1 = [
        ["PKG-1001", "15.2", "90210", "John Doe"],
        ["PKG-1002", "55.0", "90210", "Heavy Mike"], # Overweight
        ["PKG-1003", "5.0", "9021", "Bad Zip Guy"],   # Invalid Zip
        ["PKG-1004", "12.5", "90001", "Alice Smith"],
    ]
    
    data_file_2 = [
        ["PKG-2001", "48.9", "90210", "Bob Builder"],
        ["PKG-2002", "60.5", "80000", "Gym Bro"],     # Overweight
        ["PKG-2003", "2.1", "90001", "Tiny Tim"],
        ["PKG-2004", "8.0", "ABCDE", "Wrong Letters"],# Invalid Zip
    ]
    
    data_file_3 = [
        ["PKG-3001", "10.0", "33101", "Miami Vice"],
        ["PKG-3002", "50.1", "33101", "Borderline Heavy"], # Overweight
        ["PKG-3003", "50.0", "90210", "Just Right"],  # Valid (exactly 50.0 is not > 50.0)
    ]

    # Write CSVs
    with open(os.path.join(manifests_dir, "route_a.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Package_ID", "Weight_lbs", "ZipCode", "Recipient"])
        writer.writerows(data_file_1)

    with open(os.path.join(manifests_dir, "route_b.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Package_ID", "Weight_lbs", "ZipCode", "Recipient"])
        writer.writerows(data_file_2)
        
    with open(os.path.join(manifests_dir, "route_c.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Package_ID", "Weight_lbs", "ZipCode", "Recipient"])
        writer.writerows(data_file_3)

if __name__ == "__main__":
    build_env()
