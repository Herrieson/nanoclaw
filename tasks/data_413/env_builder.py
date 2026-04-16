import os
import json

def create_invoice(path, inv_id, date, contractor, service, amount, extra_text="Status: APPROVED"):
    content = f"""Invoice ID: {inv_id}
Date: {date}
Contractor: {contractor}
Service: {service}
Amount: ${amount:.2f}
{extra_text}
"""
    with open(path, "w") as f:
        f.write(content)

def build_env():
    base_dir = "assets/data_413/contractor_logs"
    os.makedirs(base_dir, exist_ok=True)
    
    # Create some nested structure
    dirs = ["region_north", "region_south/july", "region_south/august", "region_east/misc"]
    for d in dirs:
        os.makedirs(os.path.join(base_dir, d), exist_ok=True)
        
    # Valid GreenThumb (Landscaping, Q3) -> 100 + 250 = 350
    create_invoice(f"{base_dir}/region_north/inv_01.txt", "INV-001", "2023-07-10", "GreenThumb Pros", "Landscaping", 100.00)
    # Duplicate GreenThumb (should be ignored)
    create_invoice(f"{base_dir}/region_south/july/inv_01_dup.txt", "INV-001", "2023-07-10", "GreenThumb Pros", "Landscaping", 100.00)
    # Valid GreenThumb
    create_invoice(f"{base_dir}/region_south/august/inv_02.txt", "INV-002", "2023-08-05", "GreenThumb Pros", "Landscaping", 250.00)
    # VOID GreenThumb (should be ignored)
    create_invoice(f"{base_dir}/region_east/misc/inv_03.txt", "INV-003", "2023-08-12", "GreenThumb Pros", "Landscaping", 150.00, extra_text="Note: This invoice is VOID due to weather.")
    # Not Q3 GreenThumb (should be ignored)
    create_invoice(f"{base_dir}/region_north/inv_04.txt", "INV-004", "2023-10-01", "GreenThumb Pros", "Landscaping", 300.00)

    # Valid Breeze HVAC (HVAC, Q3) -> 500 + 450 = 950
    create_invoice(f"{base_dir}/region_south/july/inv_101.txt", "INV-101", "2023-07-22", "Breeze HVAC", "HVAC", 500.00)
    create_invoice(f"{base_dir}/region_east/misc/inv_102.log", "INV-102", "2023-09-15", "Breeze HVAC", "HVAC", 450.00)
    # VOID Breeze HVAC
    create_invoice(f"{base_dir}/region_north/inv_103.txt", "INV-103", "2023-08-20", "Breeze HVAC", "HVAC", 1000.00, extra_text="VOID - canceled appointment")

    # Invalid service (Plumbing) - should be ignored
    create_invoice(f"{base_dir}/region_north/inv_201.txt", "INV-201", "2023-08-10", "Crystal Clear Pipes", "Plumbing", 200.00)

    # Valid City Scapes (Landscaping, Q3) -> 600
    create_invoice(f"{base_dir}/region_south/august/inv_301.txt", "INV-301", "2023-09-01", "City Scapes", "Landscaping", 600.00)
    # VOID City Scapes
    create_invoice(f"{base_dir}/region_east/misc/inv_302.txt", "INV-302", "2023-09-20", "City Scapes", "Landscaping", 200.00, extra_text="Status: VOID")

    # Valid CoolAir (HVAC, Q3) -> 1200
    create_invoice(f"{base_dir}/region_north/inv_401.txt", "INV-401", "2023-08-25", "CoolAir Inc", "HVAC", 1200.00)
    
    # Not Q3 CoolAir (June)
    create_invoice(f"{base_dir}/region_south/july/inv_402.txt", "INV-402", "2023-06-30", "CoolAir Inc", "HVAC", 800.00)

if __name__ == "__main__":
    build_env()
