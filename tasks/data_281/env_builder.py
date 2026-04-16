import os
import random

def build_env():
    base_dir = "assets/data_281"
    os.makedirs(base_dir, exist_ok=True)
    
    logs_path = os.path.join(base_dir, "mail_logs.txt")
    
    # We will mix separators: pipe, comma, tab
    # Format: Date SEP Tracking SEP Sender SEP Dept SEP Project SEP Status
    
    data = [
        ("2023-10-01", "TRK901", "Acme Corp", "Engineering", "PRJ-TX-001", "DELIVERED"),
        ("2023-10-02", "TRK902", "BuildIt", "Architecture", "PRJ-NY-102", "DELIVERED"),
        ("2023-10-03", "TRK903", "SuppliesInc", "HR", "PRJ-TX-002", "PENDING"),
        ("2023-10-04", "TRK904", "Acme Corp", "Architecture", "PRJ-TX-003", "DELIVERED"),
        ("2023-10-05", "TRK905", "City Hall", "Engineering", "PRJ-TX-004", "DELIVERED"),
        ("2023-10-06", "TRK906", "VendorA", "Maintenance", "PRJ-TX-005", "DELIVERED"),
        ("2023-10-07", "TRK907", "VendorB", "Design", "PRJ-CA-001", "DELIVERED"),
        ("2023-10-08", "TRK908", "Acme Corp", "Engineering", "PRJ-TX-006", "RETURNED"),
        ("2023-10-09", "TRK909", "BuildIt", "Architecture", "PRJ-TX-007", "DELIVERED"),
        ("2023-10-10", "TRK910", "SuppliesInc", "HR", "PRJ-TX-008", "DELIVERED"),
        ("2023-10-11", "TRK911", "Acme Corp", "Design", "PRJ-TX-009", "DELIVERED"),
        ("2023-10-12", "TRK912", "City Hall", "Design", "PRJ-TX-010", "DELIVERED"),
        ("2023-10-13", "TRK913", "VendorA", "Engineering", "PRJ-TX-011", "DELIVERED"),
        ("2023-10-14", "TRK914", "VendorC", "Architecture", "PRJ-TX-012", "DELIVERED"),
        ("2023-10-15", "TRK915", "Acme Corp", "HR", "PRJ-TX-013", "DELIVERED"),
        ("2023-10-16", "TRK916", "BuildIt", "HR", "PRJ-TX-014", "DELIVERED")
    ]
    
    # Expected DELIVERED + PRJ-TX:
    # TRK901 -> Engineering
    # TRK904 -> Architecture
    # TRK905 -> Engineering
    # TRK906 -> Maintenance
    # TRK909 -> Architecture
    # TRK910 -> HR
    # TRK911 -> Design
    # TRK912 -> Design
    # TRK913 -> Engineering
    # TRK914 -> Architecture
    # TRK915 -> HR
    # TRK916 -> HR
    
    # Counts:
    # Architecture: 3
    # Engineering: 3
    # HR: 3
    # Design: 2
    # Maintenance: 1
    
    separators = ["|", ",", "\t"]
    
    with open(logs_path, "w", encoding="utf-8") as f:
        f.write("DATE TRACKING SENDER DEPT PROJECT STATUS (MESSY FORMAT)\n")
        f.write("----------------------------------------------------\n")
        for row in data:
            sep = random.choice(separators)
            f.write(sep.join(row) + "\n")
            
        # Add some garbage lines to test robustness
        f.write("Random garbage line that should be ignored\n")
        f.write("2023-10-17|TRK917|Unknown|Admin|PRJ-TX-015|LOST\n")

if __name__ == "__main__":
    build_env()
