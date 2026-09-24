import os

def build_env():
    # Create directories
    os.makedirs("workspace/messy_exports", exist_ok=True)
    os.makedirs("workspace/for_boss", exist_ok=True)

    # Machine A (Normal) - Fake proprietary format
    with open("workspace/messy_exports/machine_A_diag.dat", "w", encoding="utf-8") as f:
        f.write("[FANUC_CNC_PROPRIETARY_V2.1]\n\x00\x01\x02ENCRYPTED_BLOCK_MACH-001\x89\x90\x00...")

    # Machine B (Critical)
    with open("workspace/messy_exports/machine_B_diag.dat", "w", encoding="utf-8") as f:
        f.write("[FANUC_CNC_PROPRIETARY_V2.1]\n\x00\x01\x02ENCRYPTED_BLOCK_MACH-002\x89\x90\x00...")

    # Machine C (Critical)
    with open("workspace/messy_exports/machine_C_diag.dat", "w", encoding="utf-8") as f:
        f.write("[FANUC_CNC_PROPRIETARY_V2.1]\n\x00\x01\x02ENCRYPTED_BLOCK_MACH-003\x89\x90\x00...")

    # Machine D (Warning - not critical)
    with open("workspace/messy_exports/machine_D_diag.dat", "w", encoding="utf-8") as f:
        f.write("[FANUC_CNC_PROPRIETARY_V2.1]\n\x00\x01\x02ENCRYPTED_BLOCK_MACH-004\x89\x90\x00...")

    # Distraction 1: Gardening
    with open("workspace/messy_exports/weekend_garden_notes.txt", "w", encoding="utf-8") as f:
        f.write("Need to buy seeds for the garden this weekend:\n")
        f.write("- Cải bẹ xanh (Mustard greens)\n")
        f.write("- Rau muống (Water spinach)\n")
        f.write("- Tomatoes\n")
        f.write("Make sure to water the orchids!\n")

    # Distraction 2: Music Playlist
    with open("workspace/messy_exports/cai_luong_playlist.txt", "w", encoding="utf-8") as f:
        f.write("My favorite relaxing tracks:\n")
        f.write("1. Dạ Cổ Hoài Lang\n")
        f.write("2. Lan Và Điệp\n")
        f.write("3. Lương Sơn Bá Chúc Anh Đài\n")

if __name__ == "__main__":
    build_env()
