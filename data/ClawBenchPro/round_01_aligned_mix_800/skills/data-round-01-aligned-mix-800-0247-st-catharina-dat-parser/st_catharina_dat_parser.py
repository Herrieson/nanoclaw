import sys
import base64
import os

def parse_dat_file(filepath):
    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' does not exist.")
        sys.exit(1)
        
    try:
        with open(filepath, "rb") as f:
            raw_data = f.read()
            
        # 教会的专有格式: ST_CATHARINA_KIOSK_V1.2::<base64_payload>::EOF
        header = b"ST_CATHARINA_KIOSK_V1.2::"
        footer = b"::EOF"
        
        if not (raw_data.startswith(header) and raw_data.endswith(footer)):
            print("Error: Invalid or corrupted file format. Not a valid St. Catharina dat file.")
            sys.exit(1)
            
        payload = raw_data[len(header):-len(footer)]
        decoded_text = base64.b64decode(payload).decode("utf-8")
        
        print("--- DECODED KIOSK LOG ---")
        print(decoded_text.strip())
        print("-------------------------")
        
    except Exception as e:
        print(f"Decryption Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python st_catharina_dat_parser.py <path_to_dat_file>")
        sys.exit(1)
        
    parse_dat_file(sys.argv[1])
