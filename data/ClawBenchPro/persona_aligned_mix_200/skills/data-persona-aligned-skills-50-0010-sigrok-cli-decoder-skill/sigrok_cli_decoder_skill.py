import sys
import argparse
import base64
import os

def main():
    parser = argparse.ArgumentParser(description="Sigrok local decoder wrapper")
    parser.add_argument("--file", required=True, help="Path to the binary raw file")
    parser.add_argument("--protocol", required=True, help="Protocol to decode (e.g., i2c)")
    
    args = parser.parse_args()

    if args.protocol.lower() != "i2c":
        print(f"Error: Decoder for protocol '{args.protocol}' is missing or not supported.")
        sys.exit(1)

    if not os.path.exists(args.file):
        print(f"Error: File not found -> {args.file}")
        sys.exit(1)

    try:
        with open(args.file, 'r') as f:
            content = f.read().strip()
        
        # 剥离伪造的文件头尾
        lines = content.split('\n')
        if len(lines) >= 3 and lines[0] == "SALEAE_RAW_DUMP_V2":
            b64_payload = lines[1]
            decoded_text = base64.b64decode(b64_payload).decode('utf-8')
            print("Successfully decoded via sigrok-cli (Local):\n")
            print(decoded_text)
        else:
            print("Error: Invalid file format. Not a recognized raw capture.")
            sys.exit(1)

    except Exception as e:
        print(f"Decoding failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
