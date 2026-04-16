import os

def build_env():
    base_dir = "assets/data_444"
    os.makedirs(base_dir, exist_ok=True)

    supplier_notes = """
Supplier Info Dump - Sorry for the mess!

>>> NORDICBITES <<<
They sell Hakarl (Fermented Shark) for $30 per unit.
Shipping to WI is kinda steep, they charge $40 flat.
They also have Lingonberry jam but I don't need that.

>>> VIKINGEXPORTS <<<
Hakarl here is $35 per unit.
But their shipping is way better, only $10 flat rate!

>>> SPICYBOYZ <<<
Carolina Reaper Mash. Good stuff. $12 a jar.
Shipping is $15 flat rate to the US.

>>> FIRECORP <<<
Also sells Carolina Reaper Mash. Only $10 a jar! Wow!
Wait, their shipping is $40 flat. That's a rip-off.

>>> EUROFUNGI <<<
Got the Black Truffles. $80 per oz.
Shipping from Europe is $20 flat.

>>> LUXURYEATS <<<
Black Truffles for $70 per oz.
Shipping flat fee is $50.

I think that's all of them. Make sure to calculate the total cost per item by multiplying the price by how many I need, and THEN add the shipping fee for that specific supplier. 
"""

    shopping_list = """
Shopping List for the Pop-up:
- Hakarl (Fermented Shark): 5 units
- Carolina Reaper Mash: 10 jars
- Black Truffles: 2 oz
"""

    with open(os.path.join(base_dir, "supplier_notes.txt"), "w") as f:
        f.write(supplier_notes)

    with open(os.path.join(base_dir, "shopping_list.txt"), "w") as f:
        f.write(shopping_list)

if __name__ == "__main__":
    build_env()
