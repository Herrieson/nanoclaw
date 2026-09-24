import sys
import base64
import os

def decrypt_spd(input_file, output_file):
    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' not found.")
        return

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if not content.startswith("SAFEPOET_V1::"):
            print("Error: Invalid file format. Missing SAFEPOET_V1 header.")
            return
            
        b64_data = content.split("::", 1)[1]
        decoded_text = base64.b64decode(b64_data).decode('utf-8')
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(decoded_text)
            
        print(f"Success: Decrypted text saved to '{output_file}'.")
    except Exception as e:
        print(f"Decryption failed: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python safepoet_decrypter.py <input_spd_file> <output_txt_file>")
        sys.exit(1)
        
    decrypt_spd(sys.argv[1], sys.argv[2])
