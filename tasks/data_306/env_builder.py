import os
import json
import random

def build_env():
    base_dir = "assets/data_306"
    records_dir = os.path.join(base_dir, "mineral_records")
    os.makedirs(records_dir, exist_ok=True)

    # 预设的混淆数据与目标数据
    files_data = [
        # Target 1: Beryllium, Q3, Wholesale -> $45,000
        ("invoice_738.dat", "Date: 07/15/2023\nClient: ACME Corp\nMetal: Beryllium\nType: Wholesale\nAmount: $45,000.00\nNotes: Standard shipping."),
        
        # Target 2: Titanium, Q3, Wholesale -> $120,500
        ("notes_aug.txt", "Record from 2023-08-22\nWe sold a huge batch today.\nType=Wholesale\nMaterial=Titanium\nValue=$120,500\nSigned off by me."),
        
        # Target 3: Beryllium, Q3, Wholesale -> $32,000
        ("buy_log.tmp", "log entry // Sept 10 2023\ncommodity: Beryllium\ncategory: Wholesale\ntotal_usd: 32000\nstatus: cleared"),
        
        # Target 4: Titanium, Q3, Wholesale -> $88,000
        ("invoice_992.log", "2023/09/28\nWholesale Transaction\nTitanium plates.\nPrice: $88,000\nDelivered."),

        # Noise 1: Beryllium, Q3, Personal (IGNORE)
        ("personal_collection.log", "Date: 08/05/2023\nBought a nice specimen for the shelf.\nMetal: Beryllium\nType: Personal\nAmount: $400.00\nFrom a local dealer."),

        # Noise 2: Titanium, Q2, Wholesale (IGNORE)
        ("q2_sales.csv", "date,type,metal,amount\n05/10/2023,Wholesale,Titanium,50000"),

        # Noise 3: Copper, Q3, Wholesale (IGNORE)
        ("copper_aug.txt", "Date: 08/15/2023\nMetal: Copper\nType: Wholesale\nAmount: $15,000"),

        # Noise 4: Beryllium, Q4, Wholesale (IGNORE)
        ("nov_sales.dat", "Date: 11/02/2023\nMetal: Beryllium\nType: Wholesale\nAmount: $60,000"),
        
        # Noise 5: Random garbage text
        ("ramblings.txt", "Need to call the rabbi about the upcoming holidays. Also, the lathe needs a new belt. Prices of Beryllium are going up, maybe I should check the Q1 stats later.")
    ]

    for filename, content in files_data:
        file_path = os.path.join(records_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

    # Generate some random noise files to make it truly messy
    for i in range(10):
        with open(os.path.join(records_dir, f"temp_{i}.bak"), 'w') as f:
            f.write(f"backup file {i}\nnothing to see here\n")

if __name__ == "__main__":
    build_env()
