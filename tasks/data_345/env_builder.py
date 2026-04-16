import os
import json

def build_env():
    base_dir = "assets/data_345"
    invoices_dir = os.path.join(base_dir, "invoices")
    
    os.makedirs(invoices_dir, exist_ok=True)
    
    # Invoice 1: CSV format
    with open(os.path.join(invoices_dir, "inv_01.csv"), "w") as f:
        f.write("item,price\n")
        f.write("apples,12.50\n")
        f.write("premium_dates,55.00\n")
        f.write("bottled_water,10.00\n")

    # Invoice 2: TXT custom format
    with open(os.path.join(invoices_dir, "inv_02.txt"), "w") as f:
        f.write("Item: tea cups | Price: $45.00\n")
        f.write("Item: display shelf | Price: $120.00\n")
        f.write("Item: register tape | Price: $15.50\n")

    # Invoice 3: Dirty CSV (semicolon, spaces)
    with open(os.path.join(invoices_dir, "inv_03_dirty.csv"), "w") as f:
        f.write("item;price\n")
        f.write("cleaning supplies; 60.50 \n")
        f.write("trash bags; 15.00\n")
        f.write("store sign; 250.00 \n")

    # Local vendors JSON
    vendors = [
        {
            "name": "Tigris Seafood",
            "phone": "555-0101",
            "products": ["carp", "tilapia", "salmon"]
        },
        {
            "name": "Baghdad Spices & Tea",
            "phone": "555-0202",
            "products": ["black tea", "cardamom", "saffron"]
        },
        {
            "name": "American Wholesale",
            "phone": "555-0303",
            "products": ["paper towels", "soda", "pork ribs"]
        },
        {
            "name": "Green Valley Farms",
            "phone": "555-0404",
            "products": ["dates", "figs", "lamb"]
        }
    ]
    
    with open(os.path.join(base_dir, "local_vendors.json"), "w") as f:
        json.dump(vendors, f, indent=4)

if __name__ == "__main__":
    build_env()
