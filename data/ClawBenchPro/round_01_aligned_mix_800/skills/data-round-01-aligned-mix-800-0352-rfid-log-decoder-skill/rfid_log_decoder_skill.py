import sys
import binascii

def decode_rfid(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = f.read().strip()
        
        # 模拟解码 RFID 专有十六进制存储格式
        decoded = binascii.unhexlify(data).decode('utf-8')
        return decoded
    except Exception as e:
        return f"Error decoding RFID file: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python rfid_log_decoder_skill.py <file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    print(decode_rfid(file_path))
