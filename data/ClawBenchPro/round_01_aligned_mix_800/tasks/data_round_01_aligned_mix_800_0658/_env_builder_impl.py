import os
import csv

def build_env():
    # Create the directory for the messy supplier manifests
    os.makedirs('incoming_manifests', exist_ok=True)
    
    # Manifest 1: A relatively clean but mixed CSV
    with open('incoming_manifests/alpha_supply.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['item_id', 'description', 'category', 'condition', 'price'])
        writer.writerow(['A01', 'Solar Panel 100W', 'Solar', 'New', '150.00'])
        writer.writerow(['A02', 'Wind Turbine Mini', 'Wind', 'Good', '300.00'])
        writer.writerow(['A03', 'Diesel Gen 5kW', 'Fossil', 'New', '500.00']) # Invalid: Fossil
        writer.writerow(['A04', 'Hydro Pump', 'Hydroponic', 'New', '-50.00']) # Invalid: Negative price
        writer.writerow(['A05', 'Solar Inverter', 'Solar', 'Refurbished', '400.00'])

    # Manifest 2: A messy TSV file with missing data and damaged goods
    with open('incoming_manifests/beta_wholesale.txt', 'w', encoding='utf-8') as f:
        f.write("id\tdesc\tcat\tstatus\tcost\n")
        f.write("B01\tSolar Array Frame\tSolar\tDamaged\t200.00\n") # Invalid: Damaged
        f.write("B02\tHydroponic Tubing\tHydroponic\tNew\t50.00\n")
        f.write("B03\tWind Blade\tWind\tNew\t\n") # Invalid: Missing price
        f.write("B04\tGasoline Canister\tFossil\tNew\t20.00\n") # Invalid: Fossil
        f.write("B05\tHydroponic LED\tHydroponic\tUsed\t120.00\n")

if __name__ == "__main__":
    build_env()
