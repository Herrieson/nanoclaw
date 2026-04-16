import os
import binascii

def create_env():
    base_dir = "assets/data_429/vintage_tools"
    os.makedirs(base_dir, exist_ok=True)

    tools_data_1 = [
        "Model: Wrench-70A, HRC: 55, Length: 8.5",
        "Model: Hammer-B, HRC: 45, Length: 12.0",
        "Model: Screwdriver-X, HRC: 52, Length: 6.0"
    ]
    
    tools_data_2 = [
        "Model: Pliers-Q, HRC: 48, Length: 7.0",
        "Model: Wrench-72C, HRC: 60, Length: 10.0",
        "Model: Chisel-Old, HRC: 50, Length: 5.5" # exactly 50, should be excluded
    ]

    def write_dump(filename, data_list):
        filepath = os.path.join(base_dir, filename)
        with open(filepath, 'w') as f:
            f.write("=== VINTAGE TOOL TAPE DUMP v1.0 ===\n")
            f.write("INFO: Starting extraction...\n")
            
            for i, item in enumerate(data_list):
                hex_str = binascii.hexlify(item.encode('utf-8')).decode('utf-8')
                f.write(f"[RAW] {hex_str}\n")
                if i % 2 == 0:
                    f.write("CORRUPT_SECTOR: UNREADABLE DATA BLOCK AT 0x8A9F\n")
                    f.write("[RAW] 2a2a2a2a2a4552524f522a2a2a2a2a\n") # *****ERROR*****
            f.write("INFO: Dump finished with warnings.\n")

    write_dump("tape_vol1.log", tools_data_1)
    write_dump("tape_vol2.log", tools_data_2)

if __name__ == "__main__":
    create_env()
