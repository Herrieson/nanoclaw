import os
import json

def build_env():
    base_dir = "assets/data_426"
    specs_dir = os.path.join(base_dir, "draft_specs")
    os.makedirs(specs_dir, exist_ok=True)

    # Generate JSON specs
    specs = [
        {"part_id": "FW-101", "material": "Aluminum", "weight": 4.5},
        {"part_id": "LG-202", "material": "titanium", "weight": 12.1},
        {"part_id": "WS-303", "material": "Carbon Fiber"}, # Missing weight
        {"part_id": "ER-404", "weight": 8.5}, # Missing material
        {"part_id": "EN-505", "material": "TITANIUM", "weight": 35.0},
        {"part_id": "CP-606", "material": "Steel", "weight": 15.2},
        {"part_id": "FL-707", "material": "Titanium", "weight": 5.5},
        {"part_id": "VD-808"}, # Missing both
    ]

    for i, spec in enumerate(specs):
        with open(os.path.join(specs_dir, f"part_{i}.json"), "w") as f:
            json.dump(spec, f, indent=2)

    # Create buggy script
    script_content = """import json, os, csv

def process():
    files = os.listdir('draft_specs')
    with open('bom.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Part ID', 'Material', 'Weight'])
        for file in files:
            if file.endswith('.json'):
                with open(os.path.join('draft_specs', file)) as jf:
                    data = json.load(jf)
                    # This will crash if keys are missing
                    writer.writerow([data['part_id'], data['material'], data['weight']])

if __name__ == '__main__':
    process()
"""
    with open(os.path.join(base_dir, "process_drafts.py"), "w") as f:
        f.write(script_content)

if __name__ == "__main__":
    build_env()
