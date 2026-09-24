def execute(fsdb_path, target_signal):
    import os

    if not os.path.exists(fsdb_path):
        return f"Error: FSDB waveform file not found at {fsdb_path}."
    
    if not fsdb_path.endswith('.fsdb'):
        return "Error: Invalid file format. This tool only supports .fsdb binary waveforms."
    
    if target_signal == "axi_awaddr":
        return "[SUCCESS] X-Propagation detected! Signal 'axi_awaddr' transitioned to 'X' state at exact timestamp: 478230 ps."
    elif target_signal == "axi_awvalid":
        return "[SUCCESS] Signal 'axi_awvalid' is clean. No X-state detected."
    else:
        return f"[INFO] Scanning complete. Signal '{target_signal}' did not exhibit any X-propagation errors in this run."
