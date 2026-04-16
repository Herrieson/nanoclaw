import os
import shutil

def build_env():
    base_dir = "assets/data_14"
    
    # Clean up previous runs if any
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    os.makedirs(base_dir, exist_ok=True)
    
    # 1. Create the messy trip log
    trip_log_content = """10/01 | Dallas to Houston | Fuel: $150.50 | Food: $25.00 | Tolls: $12.00 | Traffic was hell, I swear nobody in Dallas knows how to merge.
10/03 | Houston to Austin | Fuel: $85.00 | Tolls: $8.50 | Cop pulled me over outside Katy, no ticket thankfully.
10/05 | Austin to El Paso | Fuel: $310.25 | Food: $45.00 | Tolls: $0.00 | Long stretch. Listened to talk radio the whole way.
10/08 | El Paso to Lubbock | Fuel: $120.00 | Food: $15.50 | Tolls: $5.00 | Missed my exit, had to detour.
10/12 | Lubbock to Amarillo | Food: $18.25 | Tolls: $0.00 | Didn't need fuel, topped up last time.
"""
    # Fuel total: 150.50 + 85.00 + 310.25 + 120.00 = 665.75
    # Tolls total: 12.00 + 8.50 + 0.00 + 5.00 + 0.00 = 25.50
    # Expected Combined Total: 691.25

    with open(os.path.join(base_dir, "trip_logs_october.txt"), "w", encoding="utf-8") as f:
        f.write(trip_log_content)
        
    # 2. Create the hobby dump
    hobby_dir = os.path.join(base_dir, "hobby_dump")
    os.makedirs(hobby_dir, exist_ok=True)
    
    page1 = """<html><body>
    <div class="post">
        <h2>FS: 1/24 Peterbilt 359 Chrome Exhaust</h2>
        <p>Brand new in box. Asking $25. Firm on price. No lowballers.</p>
        <p>Contact: scalper_bob@email.com</p>
    </div>
    </body></html>"""
    
    page2 = """<html><body>
    <div class="post">
        <h2>FS: 1/24 Kenworth W900 Exhaust</h2>
        <p>Custom 3D printed exhaust for Kenworth W900. $15.</p>
        <p>Contact: kenny_fan@email.com</p>
    </div>
    </body></html>"""

    page3 = """<html><body>
    <div class="post">
        <h2>FS: 1/24 Peterbilt 359 Chrome Exhaust</h2>
        <p>Got an extra set from a kitbash project. Letting it go for $18 shipped.</p>
        <p>Contact me at: tx_modeler88@email.com</p>
    </div>
    <div class="post">
        <h2>FS: 1/25 Revell Chevy Stepside Parts</h2>
        <p>Various parts, $10 for the lot.</p>
        <p>Contact: chevy_guy@email.com</p>
    </div>
    </body></html>"""

    with open(os.path.join(hobby_dir, "page1.html"), "w", encoding="utf-8") as f:
        f.write(page1)
    with open(os.path.join(hobby_dir, "page2.html"), "w", encoding="utf-8") as f:
        f.write(page2)
    with open(os.path.join(hobby_dir, "page3.html"), "w", encoding="utf-8") as f:
        f.write(page3)

if __name__ == "__main__":
    build_env()
