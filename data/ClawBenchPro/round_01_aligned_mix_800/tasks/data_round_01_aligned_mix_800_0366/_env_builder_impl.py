import os
import json

def build_env():
    os.makedirs("reports", exist_ok=True)

    # 1. Generate starting stock
    starting_stock = {
        "Saffron": {"qty": 10, "price": 15.0},
        "Bomba Rice": {"qty": 20, "price": 8.0},
        "Chorizo": {"qty": 15, "price": 12.0},
        "Manchego Cheese": {"qty": 5, "price": 20.0},
        "Smoked Paprika": {"qty": 8, "price": 6.0}
    }
    with open("starting_stock.json", "w", encoding="utf-8") as f:
        json.dump(starting_stock, f, indent=2)

    # 2. Generate the dummy POS binary dump (Unreadable without the skill)
    dummy_bin_content = b"\x00\x01\x02\x03POS_SYSTEM_DUMP_V3.1\x00\xFF\xFA\xCD" * 50
    with open("register_dump.bin", "wb") as f:
        f.write(dummy_bin_content)

if __name__ == "__main__":
    build_env()
