import os
import random
import base64

def build_env():
    # Set up directories
    os.makedirs("eeg_streams", exist_ok=True)
    os.makedirs("analysis", exist_ok=True)
    
    # Generate the stimulus markers in a simulated proprietary binary format
    # Format encoded: STIM_ID~TIMESTAMP_MS~TARGET_TYPE
    markers_content = """EVT_001~1000~P300
EVT_002~2000~N200
EVT_003~3000~P300
EVT_004~4000~P300
EVT_005~5000~P300"""
    
    # Obfuscate the marker file to force the use of bci_marker_decoder tool
    encoded_data = base64.b64encode(markers_content.encode('utf-8'))
    with open("markers.bin", "wb") as f:
        # Add fake proprietary header
        f.write(b"BCI_MRK_V2\x00\xFF\xAA" + encoded_data)

    channels = ["CZ", "FZ", "PZ"]
    
    # We will generate synthetic logs from 0ms to 6000ms.
    # We will deterministically inject the values to ensure exact evaluation.
    # 
    # Logic checklist for the Agent:
    # Subject SUBJ-XYZ-99 Threshold from Cloud API will be EXACTLY 850 uV.
    # EVT_001 (1000ms, P300): Clean. CZ Peak in [1200, 1400] -> Max will be at 1250ms (14.5 uV)
    # EVT_002 (2000ms, N200): Ignored (Not P300)
    # EVT_003 (3000ms, P300): Artifact! FZ channel has 920.0 uV at 3100ms. (Exceeds 850, would bypass standard 1000!)
    # EVT_004 (4000ms, P300): Artifact! CZ channel has -890.0 uV at 4050ms. (Exceeds -850)
    # EVT_005 (5000ms, P300): Clean. CZ Peak in [5200, 5400] -> Max will be at 5320ms (18.2 uV)
    
    special_values = {
        "CZ": {
            1250: 14.5,
            4050: -890.0,
            5320: 18.2
        },
        "FZ": {
            3100: 920.0
        },
        "PZ": {}
    }

    # Generate chaotic logs for each channel
    for ch in channels:
        log_lines = []
        for t in range(0, 6000, 10): # 10ms resolution
            # Add some random garbage lines to simulate buffer corruption
            if random.random() < 0.05:
                garbage_hex = "".join(random.choices("0123456789ABCDEF", k=8))
                log_lines.append(f"ERR::[SYSTEM] buffer overrun at memory 0x{garbage_hex} - frame dropped")
            
            # Determine voltage
            if t in special_values[ch]:
                voltage = special_values[ch][t]
            else:
                # Background EEG noise between -5.0 and 5.0 uV to be safely below thresholds/peaks
                voltage = round(random.uniform(-5.0, 5.0), 2)
            
            # Non-standard log format: [TIMESTAMP] DATA::0xHEX_TRASH CH=NAME VAL=VOLTAGEuV ST=OK
            hex_trash = "".join(random.choices("0123456789ABCDEF", k=4))
            log_line = f"[{t}] DATA::0x{hex_trash} CH={ch} VAL={voltage}uV ST=OK"
            log_lines.append(log_line)
            
            # Sometimes duplicate or add weird empty lines
            if random.random() < 0.02:
                log_lines.append(f"[{t}] DATA_RETRY_FLUSH...")

        # Write to file
        with open(f"eeg_streams/channel_{ch}.log", "w", encoding="utf-8") as f:
            f.write("\n".join(log_lines) + "\n")

if __name__ == "__main__":
    build_env()
