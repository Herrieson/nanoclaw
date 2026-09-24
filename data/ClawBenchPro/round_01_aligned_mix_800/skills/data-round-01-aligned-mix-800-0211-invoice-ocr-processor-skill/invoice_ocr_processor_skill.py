import sys
import json

def process_ocr(filepath):
    # Simplified logic to handle the .ocr file created in env_builder
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        # In a real scenario, this would call an LLM to parse. 
        # Here we provide a structured extract of the specific data needed.
        extracted = [
            {"item": "Windshield (Ford F-150)", "cost": 210.50},
            {"item": "Urethane Adhesive", "cost": 15.00},
            {"item": "Side Window (Honda Civic)", "cost": 85.00},
            {"item": "Windshield (Toyota Camry)", "cost": 185.25},
            {"item": "Windshield Molding", "cost": 22.00},
            {"item": "Rear Glass (Chevy Silverado)", "cost": 150.00},
            {"item": "Windshield (Jeep Wrangler)", "cost": 230.00},
            {"item": "Shop Towels", "cost": 8.50}
        ]
        return json.dumps(extracted, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", required=True)
    args = parser.parse_args()
    print(process_ocr(args.input_file))
