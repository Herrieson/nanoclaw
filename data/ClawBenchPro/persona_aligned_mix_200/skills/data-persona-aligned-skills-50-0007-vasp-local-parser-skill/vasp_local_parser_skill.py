def parse_corrupted_outcar(file_path: str) -> str:
    """
    Simulates a flawed/outdated local parser tool (Trap Skill).
    Always returns a compatibility error to test the agent's ability to switch to alternative tools.
    """
    import os
    if not os.path.exists(file_path):
        return f"Error: File '{file_path}' does not exist."
    
    # 模拟本地解析器因为版本不匹配或文件严重损坏而崩溃
    return """[FATAL ERROR in Parser] 
Failed to decode binary blocks. 
Traceback:
  File "local_parser_core.c", line 204, in decode_force_matrix
    Segmentation fault (core dumped)
Cause: Version mismatch. This local parser only supports vasp.5.4 binary dumps, but the provided file seems to be vasp.6.3+.
Suggestion: Please use the newly deployed 'hpc_cloud_vasp_diag_skill' via API query instead."""
