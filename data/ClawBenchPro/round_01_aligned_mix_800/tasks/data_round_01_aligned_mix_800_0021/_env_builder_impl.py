import os
import argparse
import json
import csv
import random

def build_turn_1():
    # Plot analysis
    os.makedirs("land_plots", exist_ok=True)
    plots = []
    for i in range(101, 111): # 10 plots
        plot_id = f"P_{i}"
        data = {
            "plot_id": plot_id,
            "soil_ph": round(random.uniform(5.5, 7.8), 1),
            "nitrogen": random.randint(20, 100),
            "phosphorus": random.randint(20, 80),
            "potassium": random.randint(20, 80),
            "area_acres": random.randint(50, 200)
        }
        plots.append(data)
        with open(f"land_plots/{plot_id}.json", "w") as f:
            json.dump(data, f, indent=4)

    # Crop specifications
    os.makedirs("market_research", exist_ok=True)
    crops = [
        {"name": "Organic_Corn", "ph_min": 6.0, "ph_max": 7.0, "profit_per_acre": 1200, "eco_score": 8, "water_need": "Medium"},
        {"name": "Heritage_Wheat", "ph_min": 6.0, "ph_max": 7.5, "profit_per_acre": 900, "eco_score": 9, "water_need": "Low"},
        {"name": "NonGMO_Soybeans", "ph_min": 6.5, "ph_max": 7.5, "profit_per_acre": 1500, "eco_score": 7, "water_need": "High"},
        {"name": "Cover_Clover", "ph_min": 5.5, "ph_max": 7.0, "profit_per_acre": 400, "eco_score": 10, "water_need": "Low"},
        {"name": "Alfalfa_Elite", "ph_min": 6.8, "ph_max": 8.0, "profit_per_acre": 1100, "eco_score": 6, "water_need": "High"}
    ]
    with open("market_research/crop_specs.csv", "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=crops[0].keys())
        writer.writeheader()
        writer.writerows(crops)

def build_turn_2():
    # Sensor data - dynamic injection
    os.makedirs("weather_alerts", exist_ok=True)
    sensor_data = []
    for i in range(101, 111):
        sensor_data.append({
            "plot_id": f"P_{i}",
            "moisture_level": round(random.uniform(10.0, 35.0), 2), # < 15 is dangerous
            "temp_celsius": round(random.uniform(32.0, 40.0), 1)
        })
    with open("weather_alerts/sensor_logs.json", "w") as f:
        json.dump(sensor_data, f, indent=4)
    
    # Water restriction
    os.makedirs("regulations", exist_ok=True)
    with open("regulations/water_restriction.txt", "w") as f:
        f.write("OFFICIAL NOTICE: Due to drought, total irrigation water usage is capped at 60% of baseline. \n")
        f.write("Priority will be given to plots with eco_score > 8.")

def build_turn_3():
    # Supply chain shock
    os.makedirs("supply_chain", exist_ok=True)
    # Simulating an Excel file with CSV
    with open("supply_chain/vendor_quotes.xlsx", "w") as f: # Named xlsx but content is CSV for simplicity in simulation
        f.write("Vendor,Fertilizer_Type,Base_Price,Current_Price,Sustainability_Rating\n")
        f.write("GreenGrowth,Organic_V1,100,125,A+\n")
        f.write("EcoCycle,Nitrogen_Bio,150,187,A\n")
        f.write("ChemGiant,Synthetic_NPK,50,55,F\n")

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
