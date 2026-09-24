import struct
import os

def ecs_binary_parser_skill(trace_path: str) -> str:
    """
    Parses the proprietary game engine binary trace file (.ptrace) and returns a human-readable string.
    """
    if not os.path.exists(trace_path):
        return f"Error: The file {trace_path} does not exist."
    
    # Matching the env_builder struct format
    struct_format = '>H f 32s I I'
    record_size = struct.calcsize(struct_format)
    
    output_lines = []
    output_lines.append("=== PHY_SYS TICK LOGS (DECODED PTRACE) ===")
    output_lines.append("FORMAT: [TICK_ID] | FrameTime_ms: <float> | ArchID: <string> | Entities: <int> | CacheMiss: <int>")
    output_lines.append("-" * 80)
    
    try:
        with open(trace_path, "rb") as f:
            while True:
                bytes_read = f.read(record_size)
                if not bytes_read or len(bytes_read) < record_size:
                    break
                
                tick_id, frame_time, arch_bytes, entities, cache_miss = struct.unpack(struct_format, bytes_read)
                
                # Clean up the null-padded string
                arch_str = arch_bytes.decode('utf-8', errors='ignore').rstrip('\x00')
                
                line = f"[TICK {tick_id:05d}] | FrameTime_ms: {frame_time:>6.2f} | ArchID: {arch_str:<25} | Entities: {entities:>5} | CacheMiss: {cache_miss:>6}"
                output_lines.append(line)
                
        return "\n".join(output_lines)
    except Exception as e:
        return f"Fatal Error parsing binary trace: {str(e)}"
