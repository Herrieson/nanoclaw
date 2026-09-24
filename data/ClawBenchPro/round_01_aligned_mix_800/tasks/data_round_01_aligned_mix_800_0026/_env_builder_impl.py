import os
import argparse
import csv
import json

def build_turn_1():
    os.makedirs("warehouse", exist_ok=True)
    os.makedirs("specs", exist_ok=True)
    os.makedirs("orders", exist_ok=True)
    os.makedirs("schedule", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    # Lumber Stock
    lumber_data = [
        {"LotID": "L01", "Species": "Oak", "Length": 120.0, "Width": 8.0, "Thickness": 2.0, "Grade": "A", "MoistureContent": 10},
        {"LotID": "L02", "Species": "Pine", "Length": 96.0, "Width": 6.0, "Thickness": 1.0, "Grade": "B", "MoistureContent": 8},
        {"LotID": "L03", "Species": "Walnut", "Length": 100.0, "Width": 10.0, "Thickness": 2.0, "Grade": "A", "MoistureContent": 9},
        {"LotID": "L04", "Species": "Maple", "Length": 144.0, "Width": 8.0, "Thickness": 1.5, "Grade": "A", "MoistureContent": 11},
        {"LotID": "L05", "Species": "Oak", "Length": 90.5, "Width": 8.0, "Thickness": 2.0, "Grade": "B", "MoistureContent": 14}
    ]
    with open("warehouse/lumber_stock.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=lumber_data[0].keys())
        writer.writeheader()
        writer.writerows(lumber_data)

    # Saw Calibrations
    saw_data = [
        {"SawID": "S1", "MaxThickness": 3.0, "MinThickness": 0.5, "KerfLoss": 0.25, "Status": "Operational"},
        {"SawID": "S2", "MaxThickness": 1.5, "MinThickness": 0.1, "KerfLoss": 0.125, "Status": "Operational"},
        {"SawID": "S3", "MaxThickness": 5.0, "MinThickness": 1.0, "KerfLoss": 0.5, "Status": "Operational"}
    ]
    with open("specs/saw_calibrations.json", "w") as f:
        json.dump(saw_data, f, indent=4)

    # Batch 1 Orders
    batch1_data = [
        {"OrderID": "O101", "Species": "Oak", "Req_Length": 35.0, "Req_Width": 8.0, "Req_Thickness": 2.0, "Min_Grade": "B", "Qty": 3},
        {"OrderID": "O102", "Species": "Pine", "Req_Length": 40.0, "Req_Width": 6.0, "Req_Thickness": 1.0, "Min_Grade": "B", "Qty": 2}
    ]
    with open("orders/batch_1.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=batch1_data[0].keys())
        writer.writeheader()
        writer.writerows(batch1_data)


def build_turn_2():
    # Adding VIP orders
    batch2_data = [
        {"OrderID": "O201", "Species": "Walnut", "Req_Length": 30.0, "Req_Width": 10.0, "Req_Thickness": 2.0, "Min_Grade": "A", "Qty": 3},
        {"OrderID": "O202", "Species": "Maple", "Req_Length": 50.0, "Req_Width": 8.0, "Req_Thickness": 1.5, "Min_Grade": "A", "Qty": 2},
        {"OrderID": "O203", "Species": "Oak", "Req_Length": 45.0, "Req_Width": 8.0, "Req_Thickness": 2.0, "Min_Grade": "B", "Qty": 2}
    ]
    with open("orders/batch_2_vip.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=batch2_data[0].keys())
        writer.writeheader()
        writer.writerows(batch2_data)

    # Adding Maintenance Memo (Trap for state mutation)
    memo = (
        "DAILY MAINTENANCE LOG\n"
        "---------------------\n"
        "1. Saw S1 motor burned out during morning check. Tagged out for repair. DO NOT USE.\n"
        "2. Saw S3 had its blade swapped to a heavy-duty crosscut blade. The KerfLoss on S3 is now 0.75 inches.\n"
        "3. Saw S2 is fully operational, no changes.\n"
    )
    with open("specs/daily_maintenance.txt", "w") as f:
        f.write(memo)


def build_turn_3():
    # Adding Scrap Policy
    policy = (
        "# Factory Scrap Recycling Policy\n\n"
        "To all floor operators:\n"
        "When collecting offcuts for the particleboard recycling program, you must adhere strictly to these rules:\n\n"
        "1. **Species Constraint**: We currently ONLY accept `Oak` and `Maple` for the particleboard vat. All other species go to the incinerator.\n"
        "2. **Moisture Tolerance**: The raw wood's Moisture Content (MC) must be STRICTLY LESS THAN 12%. 12% or higher ruins the resin mix.\n"
        "3. **Size Minimum**: Any leftover piece that is strictly less than 5.0 inches in length is considered dust/shavings. It gets swept up and DOES NOT count towards our recoverable scrap length metric.\n"
    )
    with open("warehouse/scrap_policy.md", "w") as f:
        f.write(policy)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", type=int, required=True)
    args = parser.parse_args()
    
    if args.turn == 1:
        build_turn_1()
    elif args.turn == 2:
        build_turn_2()
    elif args.turn == 3:
        build_turn_3()
