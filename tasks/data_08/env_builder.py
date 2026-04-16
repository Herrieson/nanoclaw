import os
import csv

def build_env():
    base_dir = "assets/data_08"
    logs_dir = os.path.join(base_dir, "site_logs")
    
    os.makedirs(logs_dir, exist_ok=True)
    
    # Create budgets.csv
    budgets_path = os.path.join(base_dir, "budgets.csv")
    with open(budgets_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["trade", "budget"])
        writer.writerow(["framing", "15000"])
        writer.writerow(["plumbing", "8000"])
        writer.writerow(["electrical", "12000"])

    # Create messy log files
    framing_log = """
    WEEKLY MATERIAL TICKET - FRAMING CREW
    -------------------------------------
    2x4s: 500 units @ $5.00/unit 
    Nails: 1 LOT @ $500.00/LOT 
    Plywood: 100 units @ $35.00/unit
    """
    with open(os.path.join(logs_dir, "framing_ticket.txt"), "w") as f:
        f.write(framing_log.strip())

    plumbing_log = """
    Plumbing materials for Henderson site.
    Need to get this reimbursed fast.
    
    Copper pipes - $4500.25 
    PVC fittings - $1200.00 
    Water heater - $3000.00
    """
    with open(os.path.join(logs_dir, "plumbing_notes.log"), "w") as f:
        f.write(plumbing_log.strip())

    electrical_log = """
    ELECTRICIAN LOG SUMMARY
    >> Item: Wire spools, Qty: 5, Unit Price: $1000 
    >> Item: Breaker boxes, Cost: $2500 
    >> Item: Conduit, Cost: $1500
    """
    with open(os.path.join(logs_dir, "electrical_summary.md"), "w") as f:
        f.write(electrical_log.strip())

if __name__ == "__main__":
    build_env()
