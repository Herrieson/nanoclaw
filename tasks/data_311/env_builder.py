import os

def build_env():
    base_dir = "assets/data_311"
    os.makedirs(base_dir, exist_ok=True)

    inventory_data = """ID|Product_Name|Category|Stock|Reorder_Level|Price
101|Whey Protein Isolate|Health_Supplements|15|20|29.99
102|Organic Apples|Produce|100|50|1.99
103|Daily Multivitamins|Health_Supplements|50|10|15.99
104|Creatine Monohydrate|Health_Supplements|2|15|22.50
105|Pre-workout Explosive|Health_Supplements|8|10|35.00
106|Almond Milk|Dairy|20|15|4.50
107|BCAA Recovery|Health_Supplements|12|12|19.99
108|Fish Oil Omega 3|Health_Supplements|5|25|12.00
109|Energy Drink Case|Beverages|40|20|24.00
"""
    with open(os.path.join(base_dir, "inventory_raw.dat"), "w", encoding="utf-8") as f:
        f.write(inventory_data)

    team_chat = """[09:00] Mike: Hey Jess, about that workshop. I can do Monday 10:00-12:00 or Tuesday 14:00-16:00.
[09:15] Sarah: Tuesday afternoon works best for me, like 13:00-15:00. I have a shift before that.
[09:30] Dave: I'm unloading trucks until Tuesday 14:00, but I'm completely free after that until 17:00.
[10:05] Anna: I'm swamped this week. Tuesday 14:00-15:00 is literally my only gap!
[10:12] Tom: I can join on Wednesday morning, or Tuesday anytime between 14:00 and 18:00.
[10:45] Jess: Guys, make sure you show up. It's important for your lower back health!
"""
    with open(os.path.join(base_dir, "team_chat.txt"), "w", encoding="utf-8") as f:
        f.write(team_chat)

if __name__ == "__main__":
    build_env()
