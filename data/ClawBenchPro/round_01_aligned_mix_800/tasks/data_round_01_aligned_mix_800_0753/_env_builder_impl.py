import os

def build_env():
    os.makedirs("receipts", exist_ok=True)
    os.makedirs("church_funds", exist_ok=True)
    
    with open("receipts/batch_01.csv", "w") as f:
        f.write("Item,Price\n")
        f.write("Pecan Pie,15.50\n")
        f.write("Sweet Tea Jug,5.00\n")
        f.write("Pump 4 Unleaded,42.00\n")
        f.write("Marlboro Lights,8.50\n")
        
    with open("receipts/scribbles.txt", "w") as f:
        f.write("Crazy day today. The kids were running around everywhere.\n")
        f.write("Sold a whole tray of Mary's brownies for 20.00.\n")
        f.write("Also bought 10w30 motor oil for the Chevy, cost me 6.50.\n")
        f.write("Someone bought 3 dozen chocolate chip cookies: 12.00 total.\n")

    with open("receipts/shift_log_old.csv", "w") as f:
        f.write("Transaction,Amount\n")
        f.write("Diesel Fuel,65.00\n")
        f.write("Scratch-off Tickets,10.00\n")
        f.write("Car Wash,8.00\n")

    with open("receipts/sunday_morning.txt", "w") as f:
        f.write("Church bake sale started slow.\n")
        f.write("Mrs. Higgins bought a Lemon Pound Cake: 18.00\n")
        f.write("Donation to the youth choir: 5.00 (Wait, don't count donations as bake sale items, Pastor said to keep that separate).\n")

if __name__ == "__main__":
    build_env()
