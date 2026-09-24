import sys
import binascii

def decode_badge(filepath):
    try:
        with open(filepath, 'r') as f:
            hex_data = f.read().strip()
        decoded_text = binascii.unhexlify(hex_data).decode('utf-8')
        return f"[SUCCESS] Decoded Badge Data:\n\n{decoded_text}"
    except FileNotFoundError:
        return f"[ERROR] File not found: {filepath}"
    except binascii.Error:
        return "[ERROR] Invalid format. File does not appear to be a valid .pa_badge encrypted file."
    except Exception as e:
        return f"[ERROR] Unexpected error decoding badge: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("[ERROR] Usage: python3 pa_badge_decoder.py <filepath>")
    else:
        print(decode_badge(sys.argv[1]))
