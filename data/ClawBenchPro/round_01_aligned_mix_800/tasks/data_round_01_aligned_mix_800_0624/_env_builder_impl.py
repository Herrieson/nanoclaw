import os
import csv

def build_env():
    os.makedirs('raw_data', exist_ok=True)
    
    # Write messy RSVP logs with duplicates and different statuses
    with open('raw_data/rsvps.log', 'w') as f:
        f.write("[2023-10-01] Name: Alice M. | Status: Confirmed | Extra: 1\n")
        f.write("[2023-10-01] Name: Bob | Status: Declined | Extra: 0\n")
        f.write("[2023-10-02] Name: Charlie | Status: Confirmed | Extra: 2\n")
        f.write("[2023-10-02] Name: David K. | Status: Confirmed | Extra: 0\n")
        f.write("[2023-10-03] Name: Alice M. | Status: Confirmed | Extra: 1\n") # Duplicate
        f.write("[2023-10-03] Name: Eve | Status: Pending | Extra: 1\n")
        f.write("[2023-10-04] Name: Frank | Status: Confirmed | Extra: 0\n")

    # Write artifacts CSV
    with open('raw_data/artifacts.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['GuestName', 'Artifact', 'Region'])
        writer.writerow(['Alice M.', 'Ming Dynasty Vase', 'Asia'])
        writer.writerow(['Bob', 'Celtic Brooch', 'Europe'])
        writer.writerow(['David K.', 'Aztec Calendar Stone', 'Americas'])
        writer.writerow(['Eve', 'Victorian Teacup', 'Europe'])
        # Charlie is missing from artifacts entirely
        # Frank is missing from artifacts entirely

if __name__ == "__main__":
    build_env()
