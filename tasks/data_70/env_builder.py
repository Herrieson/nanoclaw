import os
import shutil

def build_env():
    base_dir = "assets/data_70/home_lab"
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    
    os.makedirs(base_dir, exist_ok=True)
    os.makedirs(os.path.join(base_dir, "batch1"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "batch2", "nested"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "personal"), exist_ok=True)

    # Write decoy files
    with open(os.path.join(base_dir, "personal", "gym_log.txt"), "w") as f:
        f.write("Squats: 3x10\nDeadlifts: 5x5\nHR max: 180bpm\nNote: Need more chalk.")

    with open(os.path.join(base_dir, "batch1", "notes.txt"), "w") as f:
        f.write("Remember to buy Tris-HCl buffer and more pipettes.\nAlso call mom for Shabbat dinner.")
        
    with open(os.path.join(base_dir, "batch2", "shopping.txt"), "w") as f:
        f.write("Almond milk\nProtein powder\nApples\nChicken breast")

    # Write sequence files
    def write_seq(path, seq_id, seq):
        with open(path, "w") as f:
            f.write(f">{seq_id}\n{seq}\n")

    # GC: 6/12 = 50.00% -> Ignore
    write_seq(os.path.join(base_dir, "batch1", "sample_A.txt"), "SEQ_001", "ATGCATGCATGC") 
    
    # GC: 8/10 = 80.00% -> Keep
    write_seq(os.path.join(base_dir, "batch1", "sample_B.txt"), "SEQ_002", "GGCCGGCCAT") 
    
    # GC: 0/10 = 0.00% -> Ignore
    write_seq(os.path.join(base_dir, "batch2", "sample_C.txt"), "SEQ_003", "ATATATATAT") 
    
    # GC: 10/10 = 100.00% -> Keep
    write_seq(os.path.join(base_dir, "batch2", "nested", "sample_D.txt"), "SEQ_004", "GCGCGCGCGC") 
    
    # GC: 2/4 = 50.00% -> Ignore
    write_seq(os.path.join(base_dir, "sample_E.txt"), "SEQ_005", "ATGC") 
    
    # GC: 5/10 = 50.00% -> Ignore
    write_seq(os.path.join(base_dir, "batch2", "nested", "sample_F.txt"), "SEQ_006", "GGGGGAAAAA") 
    
    # GC: 7/12 = 58.33% -> Keep
    write_seq(os.path.join(base_dir, "batch1", "sample_G.txt"), "SEQ_007", "CGCGCGCGAAAA") 
    
    # GC: 6/11 = 54.54% -> Ignore (< 55%)
    write_seq(os.path.join(base_dir, "personal", "sample_H.txt"), "SEQ_008", "GCGCGCATATA") 

if __name__ == "__main__":
    build_env()
