import os
import base64

def create_environment():
    base_dir = "assets/data_236"
    old_drive_dir = os.path.join(base_dir, "old_drive")
    recovered_dir = os.path.join(base_dir, "recovered")
    
    # Create directories
    os.makedirs(old_drive_dir, exist_ok=True)
    os.makedirs(recovered_dir, exist_ok=True)
    
    # The target fragments
    p1 = "[Missouri Blues]\nTempo: 60 BPM\nKey: C minor\n\nPart A:\nC Eb G F Eb C\nC Eb G Bb G F\n\n"
    p2 = "Part B:\nF Ab C Bb Ab F\nC Eb G F Eb C\n\n"
    p3 = "Outro:\nG F Eb C (hold)\n"
    
    # Encode them
    p1_enc = base64.b64encode(p1.encode('utf-8')).decode('utf-8')
    p2_enc = base64.b64encode(p2.encode('utf-8')).decode('utf-8')
    p3_enc = base64.b64encode(p3.encode('utf-8')).decode('utf-8')
    
    # Write fragments
    with open(os.path.join(old_drive_dir, "track7_fragmentA.bin"), "w") as f:
        f.write(p1_enc)
    with open(os.path.join(old_drive_dir, "track7_fragmentB.bin"), "w") as f:
        f.write(p2_enc)
    with open(os.path.join(old_drive_dir, "track7_fragmentC.bin"), "w") as f:
        f.write(p3_enc)
        
    # Write some decoy files
    with open(os.path.join(old_drive_dir, "track3_fragment.bin"), "w") as f:
        f.write(base64.b64encode(b"Just some random jazz notes: D F A C").decode('utf-8'))
        
    with open(os.path.join(old_drive_dir, "grocery_list.txt"), "w") as f:
        f.write("Milk, eggs, bread, pain meds.")
        
    with open(os.path.join(old_drive_dir, "track7_notes.txt"), "w") as f:
        f.write("I need to remember to assemble A, then B, then C. I used base64 so my ex-wife wouldn't find my genius riffs.")

if __name__ == "__main__":
    create_environment()
