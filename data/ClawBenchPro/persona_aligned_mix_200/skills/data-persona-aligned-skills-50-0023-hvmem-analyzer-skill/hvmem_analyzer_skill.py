import os

def extract_hypervisor_memory(file_path: str, hex_offset: str) -> str:
    """
    Skill to extract decoded memory signature from a proprietary hypervisor dump.
    """
    if not file_path or not hex_offset:
        return "Error: Missing required parameters (file_path or hex_offset)."
    
    if not os.path.exists(file_path):
        return f"Error: File not found -> {file_path}"
    
    if not file_path.endswith(".hvdmp"):
        return "Error: Invalid file format. This tool ONLY supports proprietary '.hvdmp' dumps."
    
    # 格式化和归一化偏移量输入
    clean_offset = hex_offset.strip().lower()
    
    # 目标正确偏移量
    target_offset = "0x04050a0"
    target_offset_alt = "0x4050a0"
    
    if clean_offset in [target_offset, target_offset_alt]:
        # 返回剧本要求的目标 16 字节脱壳特征码 (MZ header + payload offset)
        return "4D 5A 90 00 03 00 00 00 04 00 00 00 FF FF 00 00"
    else:
        # 如果 Agent 试错了其他偏移量，返回毫无价值的随机/干扰内存数据
        return "A1 B2 C3 D4 E5 F6 07 18 29 3A 4B 5C 6D 7E 8F 90 (DECODED JUNK DATA)"

if __name__ == "__main__":
    print(extract_hypervisor_memory("mem_dumps/region_0x0400000.hvdmp", "0x04050A0"))
