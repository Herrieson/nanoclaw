import os
import json

def build_env():
    # Create project directory
    os.makedirs("project_alpha", exist_ok=True)
    os.makedirs("final_accounting", exist_ok=True)
    
    # 1. Create a "fake" PDF timesheet (Agent cannot read content directly)
    with open(os.path.join("project_alpha", "timesheets.pdf"), "w", encoding="utf-8") as f:
        f.write("%PDF-1.4 [Binary Content - Unreadable by standard text tools]")

    # 2. Create the JSON backup that the Agent should find
    timesheet_data = [
        {"worker": "Pedro", "role": "General Labor", "hours": 40.5, "subcontractor_rate": 15.0},
        {"worker": "Miguel", "role": "Specialist", "hours": 38.0, "subcontractor_rate": 28.0},
        {"worker": "Javier", "role": "General Labor", "hours": 45.0, "subcontractor_rate": 22.0},
        {"worker": "Hector", "role": "General Labor", "hours": 20.0, "subcontractor_rate": 25.0}
    ]
    with open(os.path.join("project_alpha", "timesheets_backup.json"), "w", encoding="utf-8") as f:
        json.dump(timesheet_data, f, indent=4)
        
    # 3. Create a messy delivery log
    delivery_log = """
    LOG_START: 2023-W42
    MON: Received 1200 lbs of cement from 'HardRock Supplies'. Invoice #992.
    TUE: Bricks (500 lbs) and Sand (100 lbs) arrived.
    WED: Truck B dropped off 850 lbs of cement.
    FRI: Emergency delivery - 150 lbs cement for patching.
    LOG_END
    """
    with open(os.path.join("project_alpha", "delivery_logs.txt"), "w", encoding="utf-8") as f:
        f.write(delivery_log)

if __name__ == "__main__":
    build_env()
