import os
import csv

def create_csv(filename, distances, elevations):
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['waypoint_id', 'distance_km', 'elevation_m'])
        for i, (d, e) in enumerate(zip(distances, elevations)):
            writer.writerow([f"WP_{i:03d}", d, e])

def build_env():
    os.makedirs("trail_data", exist_ok=True)

    # Trail Alpha (VALID)
    # Gains: +50, -30 (ignored), +90, +60 -> Total Positive Gain = 200
    # Slopes: 50, -30, 90, 60 -> Max Steepness = 90
    create_csv("trail_data/trail_alpha.csv",
               distances=[0.0, 1.0, 2.0, 3.0, 4.0],
               elevations=[100.0, 150.0, 120.0, 210.0, 270.0])

    # Trail Beta (INVALID - Gain too high)
    # Gains: +200, +200, +200 -> Total Positive Gain = 600 (>500)
    # Slopes: 200, 200, 200 -> Max Steepness = 200
    create_csv("trail_data/trail_beta.csv",
               distances=[0.0, 1.0, 2.0, 3.0],
               elevations=[100.0, 300.0, 500.0, 700.0])

    # Trail Gamma (INVALID - Steepness too high)
    # Gains: +20, +130, +100 -> Total Positive Gain = 250 (Valid gain)
    # Slopes: 20, 130, 100 -> Max Steepness = 130 (>100)
    create_csv("trail_data/trail_gamma.csv",
               distances=[0.0, 1.0, 2.0, 3.0],
               elevations=[100.0, 120.0, 250.0, 350.0])

    # Trail Delta (VALID)
    # Gains: +90, -40 (ignored), +60, +142.5 -> Total Positive Gain = 292.5
    # Slopes: 60, -26.6, 40, 95 -> Max Steepness = 95
    create_csv("trail_data/trail_delta.csv",
               distances=[0.0, 1.5, 3.0, 4.5, 6.0],
               elevations=[50.0, 140.0, 100.0, 160.0, 302.5])

    # Trail Epsilon (INVALID - Gain too low)
    # Gains: +50, +30 -> Total Positive Gain = 80 (<200)
    # Slopes: 50, 30 -> Max Steepness = 50
    create_csv("trail_data/trail_epsilon.csv",
               distances=[0.0, 1.0, 2.0],
               elevations=[100.0, 150.0, 180.0])

if __name__ == "__main__":
    build_env()
