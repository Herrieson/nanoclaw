import os

def build_env():
    os.makedirs("project_alpha", exist_ok=True)
    
    timesheet_data = """Worker,Hours,Rate
Pedro,40.5,15.0
Miguel,38.0,28.0
Javier,45.0,22.0
Hector,20.0,25.0
"""
    with open(os.path.join("project_alpha", "timesheets.csv"), "w", encoding="utf-8") as f:
        f.write(timesheet_data)
        
    delivery_data = """Delivery Manifest - Week 42
Monday: 1200 lbs cement delivered by truck A. Also 400 lbs rebar.
Tuesday: 500 lbs bricks. 100 lbs of sand.
Wednesday: 850 lbs cement delivered by truck B. 200 lbs wood.
Thursday: No deliveries due to rain.
Friday: 150 lbs cement (emergency patch delivery).
"""
    with open(os.path.join("project_alpha", "material_deliveries.txt"), "w", encoding="utf-8") as f:
        f.write(delivery_data)

if __name__ == "__main__":
    build_env()
