import os

def build_env():
    base_dir = "assets/data_258"
    os.makedirs(base_dir, exist_ok=True)

    phone_dump_content = """
    [2023-11-01 14:02] Mike: Hey you covering my shift tomorrow?
    [2023-11-01 14:05] Me: Yeah whatever.
    [2023-11-02 09:15] Unknown: Is this the guy who sells wood carvings?
    [2023-11-02 09:20] Me: Yea.
    [2023-11-03 16:45] Sarah: Don't forget to pick up the kids.
    [2023-11-04 11:10] Jimmy: Hey man, saw your ad at the hardware store. Looking for a custom oak crib for my incoming kid. You do that?
    [2023-11-04 11:45] Me: Yea I can do oak. $500 labor plus materials.
    [2023-11-04 12:00] Jimmy: Sounds fair. Call me at 555-0192 when you get the wood, or shoot an email to jim.hawkins_78@email.com.
    [2023-11-05 08:30] Me: k.
    [2023-11-06 18:22] Spam: YOU WON A CRUISE!
    """
    
    with open(os.path.join(base_dir, "phone_dump.txt"), "w") as f:
        f.write(phone_dump_content.strip())

    receipts_content = """
    HOME DEPOT - Store #4921
    Date: 11/05/2023
    -------------------------
    Oak boards (4x)         $ 145.50
    Work Boots (Steel toe)  $  85.00
    Box of 2.5" screws      $  12.99
    Wood glue               $   6.00
    Dark Walnut Stain       $  18.25
    Burger King Lunch       $   8.50
    -------------------------
    TOTAL                   $ 276.24
    """
    
    with open(os.path.join(base_dir, "receipts_nov.log"), "w") as f:
        f.write(receipts_content.strip())

if __name__ == "__main__":
    build_env()
