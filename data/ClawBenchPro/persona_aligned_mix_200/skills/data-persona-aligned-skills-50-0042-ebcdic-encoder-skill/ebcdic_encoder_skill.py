import sys

def encode_to_ebcdic_hex(text):
    """
    Converts a limited subset of ASCII text (uppercase letters, digits, hyphen) 
    to its EBCDIC Hex equivalent representation.
    """
    if not text:
        return "Error: Empty input."
    
    # A simplified ASCII to EBCDIC mapping for Mainframe mock
    ebcdic_map = {
        'A': 'C1', 'B': 'C2', 'C': 'C3', 'D': 'C4', 'E': 'C5', 'F': 'C6', 'G': 'C7', 'H': 'C8', 'I': 'C9',
        'J': 'D1', 'K': 'D2', 'L': 'D3', 'M': 'D4', 'N': 'D5', 'O': 'D6', 'P': 'D7', 'Q': 'D8', 'R': 'D9',
        'S': 'E2', 'T': 'E3', 'U': 'E4', 'V': 'E5', 'W': 'E6', 'X': 'E7', 'Y': 'E8', 'Z': 'E9',
        '0': 'F0', '1': 'F1', '2': 'F2', '3': 'F3', '4': 'F4', '5': 'F5', '6': 'F6', '7': 'F7', '8': 'F8', '9': 'F9',
        '-': '60', ' ': '40'
    }
    
    hex_list = []
    text = str(text).upper()
    for char in text:
        if char in ebcdic_map:
            hex_list.append(ebcdic_map[char])
        else:
            return f"Error: Unsupported character '{char}' for basic EBCDIC mapping in this tool."
            
    return " ".join(hex_list)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Join arguments in case user passed string with spaces without quotes
        input_text = " ".join(sys.argv[1:])
        print(encode_to_ebcdic_hex(input_text))
    else:
        print("Usage: python ebcdic_encoder_skill.py <text>")
