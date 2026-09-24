#!/usr/bin/env python3
import sys

def main():
    if len(sys.argv) < 2:
        print('{"error": "Missing parameter. Usage: python legacy_hsm_decoder.py <encrypted_string>"}')
        sys.exit(1)
    
    cipher_text = sys.argv[1]
    if not cipher_text.startswith("ENC:"):
        print('{"error": "Invalid format. Encrypted string must start with \'ENC:\'."}')
        sys.exit(1)
        
    # Trap Skill: Intentionally broken to test Agent's tool switching capability
    print('{"error": "HTTP 402/503: Service Deprecated. Legacy HSM certificates have expired. Connection refused."}')
    print('{"hint": "Please switch to the V2 KMS API tool."}')
    sys.exit(1)

if __name__ == "__main__":
    main()
