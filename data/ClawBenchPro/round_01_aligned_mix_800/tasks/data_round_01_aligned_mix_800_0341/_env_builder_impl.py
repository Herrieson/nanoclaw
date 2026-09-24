import os
import csv

def build_env():
    # Only creating the invoices directory. 
    # approved_rates.csv is deliberately removed to force the use of ERP Skills.
    os.makedirs("invoices", exist_ok=True)

    # Invoice 1: Correct billing
    with open("invoices/smith_builders.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Task", "Hours Logged", "Billed Rate"])
        writer.writerow(["Framing", "10", "50.00"])
        writer.writerow(["Drywall", "20", "50.00"])

    # Invoice 2: Overbilling (Billed $85 instead of $75)
    with open("invoices/jones_electrical.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Task", "Hours Logged", "Billed Rate"])
        writer.writerow(["Wiring Phase 1", "15", "85.00"])
        writer.writerow(["Panel Installation", "5", "85.00"])

    # Invoice 3: Correct billing
    with open("invoices/taylor_plumbing.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Task", "Hours Logged", "Billed Rate"])
        writer.writerow(["Pipe fitting", "10", "65.00"])

    # Invoice 4: Overbilling (Billed $95 instead of $90)
    with open("invoices/apex_roofing.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Task", "Hours Logged", "Billed Rate"])
        writer.writerow(["Shingle laying", "8", "95.00"])
        writer.writerow(["Gutter install", "4", "95.00"])

if __name__ == "__main__":
    build_env()
