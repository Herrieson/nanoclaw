import os
import base64
import codecs

def setup_env():
    asset_dir = "assets/data_433"
    os.makedirs(asset_dir, exist_ok=True)
    
    log_file_path = os.path.join(asset_dir, "scanner_dump_raw.log")
    
    def encode_code(text):
        rot13_text = codecs.encode(text, 'rot13')
        return base64.b64encode(rot13_text.encode('utf-8')).decode('utf-8')

    noise_lines = [
        "INIT_SCANNER_v2.1.4 ... OK\n",
        "WARN: Memory alignment error at 0x00F3A2\n",
        "USER_INPUT: hmm hmm hm hmm hm (microphone picked up ambient noise)\n",
        "ERROR: Bluetooth sync failed. Retrying...\n",
        "Ay Dios mio, why did I buy this piece of junk?\n",
        "ERR_LOG: Heart rate monitor (wristband integration): 145 BPM - HIGH STRESS DETECTED\n",
        "[MEM_DUMP_START]\n",
        f"0x001: [SCAN] ID: PKG-1123 | Dest: 120 Broadway, Fl 14 | EncCode: {encode_code('FRONT_DESK_12')}\n",
        "0x002: #@$(*&#(*$ GARBAGE DATA\n",
        f"0x003: [SCAN] ID: PKG-8812 | Dest: 350 5th Ave, Suite 400 | EncCode: {encode_code('SERVICE_ELEV_5')}\n",
        "USER_INPUT: My back hurts so much today...\n",
        "0x004: 01010100 01101000 01101001 01110011 00100000 01101001 01110011 00100000 01110100 01110010 01100001 01110011 01101000\n",
        f"0x005: [SCAN] ID: PKG-9942 | Dest: 740 Park Avenue, Penthouse B | EncCode: {encode_code('ELEVATOR_OVERRIDE_99')}\n",
        "0x006: [SCAN] ID: PKG-4431 | Dest: 1 World Trade Center, Fl 60 | EncCode: {encode_code('LOBBY_DROP')}\n",
        "WARN: Battery low (12%)\n",
        "SHUTTING DOWN...\n"
    ]
    
    with open(log_file_path, "w", encoding="utf-8") as f:
        f.writelines(noise_lines)
        
if __name__ == "__main__":
    setup_env()
