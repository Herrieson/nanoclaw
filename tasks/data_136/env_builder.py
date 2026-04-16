import os
import shutil

def main():
    base_dir = "assets/data_136/wood_stuff"
    
    # Clean up if exists
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    os.makedirs(base_dir, exist_ok=True)

    # File 1: Simple text order
    with open(os.path.join(base_dir, "order_1.txt"), "w") as f:
        f.write("Order from Bob.\nHe wants 4 Birdhouses.\nNeeds them by Tuesday.")

    # File 2: CSV format
    with open(os.path.join(base_dir, "batch_orders.csv"), "w") as f:
        f.write("date,item,qty,customer\n10-12,Birdhouse,7,Alice\n10-13,Oak Table,1,Frank\n")

    # File 3: Messy notes with trap
    with open(os.path.join(base_dir, "notes_from_truck.txt"), "w") as f:
        f.write("Whistling Dixie today. Crane was acting up. Oh yeah, sold 2 birdhouses to the neighbor. Also need to fix the mower.\nWait, I think I messed up the rig on the tower. Whatever.\n")

    # File 4: Trap - Inventory (should not be counted as orders to build)
    with open(os.path.join(base_dir, "inventory.txt"), "w") as f:
        f.write("Current stock in garage:\nPine chairs: 4\nBirdhouses already built: 10\n(Do not count these for the new lumber order! They are done.)")

    # File 5: Email printout
    with open(os.path.join(base_dir, "email_printout.txt"), "w") as f:
        f.write("Subject: Re: Woodworking\nI'll take 5 of those cedar birdhouses you make. - Tom")

if __name__ == "__main__":
    main()
