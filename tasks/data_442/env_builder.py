import os

def build_env():
    base_dir = "assets/data_442"
    logs_dir = os.path.join(base_dir, "workshop_logs")
    
    # Create directories
    os.makedirs(os.path.join(logs_dir, "2021"), exist_ok=True)
    os.makedirs(os.path.join(logs_dir, "2022"), exist_ok=True)
    os.makedirs(os.path.join(logs_dir, "2023"), exist_ok=True)
    
    # Create log files with data
    log1 = """Wood: Oak, Thickness: 2, Width: 4, Length: 36, Qty: 10, Price: 6.00
Wood: Pine, Thickness: 1, Width: 6, Length: 48, Qty: 20, Price: 2.50
Wood: Maple, Thickness: 1.5, Width: 5, Length: 40, Qty: 4, Price: 4.00
"""
    
    log2 = """Wood: Walnut, Thickness: 1.5, Width: 8, Length: 60, Qty: 5, Price: 9.00
Wood: Oak, Thickness: 1, Width: 12, Length: 24, Qty: 2, Price: 5.00
"""

    log3 = """Wood: Cherry, Thickness: 2, Width: 6, Length: 48, Qty: 8, Price: 7.00
Wood: Walnut, Thickness: 2, Width: 4, Length: 36, Qty: 6, Price: 8.50
Wood: Pine, Thickness: 2, Width: 4, Length: 96, Qty: 15, Price: 2.00
"""

    with open(os.path.join(logs_dir, "2021", "batch1.txt"), "w") as f:
        f.write(log1)
        
    with open(os.path.join(logs_dir, "2022", "notes.log"), "w") as f:
        f.write(log2)
        
    with open(os.path.join(logs_dir, "2023", "salvage.txt"), "w") as f:
        f.write(log3)

if __name__ == "__main__":
    build_env()
