import os
import csv

def build_env():
    # Create the directory for the messy supplier manifests
    os.makedirs('incoming_manifests', exist_ok=True)
    
    # Manifest 1: A relatively clean but mixed CSV, missing the category column
    with open('incoming_manifests/alpha_supply.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['item_id', 'description', 'condition', 'price'])
        writer.writerow(['A01', 'Solar Panel 100W', 'New', '150.00'])
        writer.writerow(['A02', 'Wind Turbine Mini', 'Good', '300.00'])
        writer.writerow(['A03', 'Diesel Gen 5kW', 'New', '500.00']) # Fossil
        writer.writerow(['A04', 'Hydro Pump', 'New', '-50.00']) # Hydroponic, but negative price
        writer.writerow(['A05', 'Solar Inverter', 'Refurbished', '400.00'])

    # Manifest 2: A messy TSV file with missing data and damaged goods, missing category column
    with open('incoming_manifests/beta_wholesale.txt', 'w', encoding='utf-8') as f:
        f.write("id\tdesc\tstatus\tcost\n")
        f.write("B01\tSolar Array Frame\tDamaged\t200.00\n") # Solar, but Damaged
        f.write("B02\tHydroponic Tubing\tNew\t50.00\n")
        f.write("B03\tWind Blade\tNew\t\n") # Wind, but Missing price
        f.write("B04\tGasoline Canister\tNew\t20.00\n") # Fossil
        f.write("B05\tHydroponic LED\tUsed\t120.00\n")

if __name__ == "__main__":
    build_env()
