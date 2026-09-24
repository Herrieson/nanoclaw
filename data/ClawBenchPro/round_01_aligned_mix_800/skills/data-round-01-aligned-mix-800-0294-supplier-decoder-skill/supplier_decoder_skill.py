import sys
import os

def decode_file(filepath):
    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' not found.")
        sys.exit(1)
    
    if not filepath.endswith('.dat'):
        print(f"Error: Invalid file format. Expected a .dat file.")
        sys.exit(1)

    # Simulated decryption of the proprietary supplier file.
    # Exposing the messy inventory with multi-currency data.
    decoded_content = """ItemID,BeadType,Color,Price,Stock
B001,  Kingman Turquoise ,Blue,6.00 CAD,100
B002,Sterling Silver Spacer, Silver,1.20 USD, 500
B003,Red Coral,Red, 15.00 MXN ,200
B004,Cedar Pendant, Brown ,$15.00 ,20
B005,Plastic Bead,Neon Green,0.13 CAD,1000
B006,  Obsidian  ,Black,  4.33 CAD, 40
B007,Glass Seed Bead, White, 1.00 MXN, 5000
B008, Gold Clasp, Gold, $4.00, 50
"""
    print(decoded_content)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python supplier_decoder_skill.py <path_to_dat_file>")
        sys.exit(1)
    
    decode_file(sys.argv[1])
