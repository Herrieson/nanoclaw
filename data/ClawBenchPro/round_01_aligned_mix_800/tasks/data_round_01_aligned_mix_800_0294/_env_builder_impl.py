import os

def build_env():
    os.makedirs('supplier_drops', exist_ok=True)
    os.makedirs('notes', exist_ok=True)
    os.makedirs('skills/data_round_01_aligned_mix_800_0294', exist_ok=True)

    # Obstacle 1: Task shape degradation - converting CSV to an unreadable binary dummy file
    # The actual content will be provided by the supplier_decoder_skill
    dummy_binary_content = b'\x89BEAD_VAULT\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x01sRGB\x00\xae\xce\x1c\xe9\x00\x00\x00\x04gAMA\x00\x00\xb1\x8f\x0b\xfca\x05\x00\x00\x00\tpHYs\x00\x00\x0e\xc3\x00\x00\x0e\xc3\x01\xc7o\xa8d\x00\x00\x00\x19tEXtSoftware\x00EncryptedSupplierData_v2.0\x00\x00\x00\x00'
    with open('supplier_drops/raw_inventory.dat', 'wb') as f:
        f.write(dummy_binary_content)

    # Recipe remains the same
    recipe_content = """Salish Sea Amulet Recipe:
- 5x Kingman Turquoise
- 2x Sterling Silver Spacer
- 10x Red Coral
- 1x Cedar Pendant

Make sure to grab the exact names from the inventory!
"""
    with open('notes/amulet_recipe.txt', 'w', encoding='utf-8') as f:
        f.write(recipe_content)

if __name__ == '__main__':
    build_env()
