import time

def dve_extractor(file_path: str, time_start_ps: int, time_end_ps: int) -> str:
    """
    Trap skill: A legacy EDA tool that always fails due to license server issues.
    This tests the agent's ability to switch to alternative skills when encountering realistic infrastructure failures.
    """
    
    # 模拟启动工具的延迟
    time.sleep(1.5)
    
    # 返回一个典型的 FlexLM License 服务器无响应或授权过期的错误
    error_msg = """
DVE Extractor (Version K-2015.09) - Copyright (c) 1991-2015 by Synopsys, Inc.
Loading waveform database...
Initializing Discovery Visual Environment...

[FATAL ERROR]: FlexLM License checkout failed.
Feature: DVE-2015
License path: 27000@flexlm.internal.farm.local;
FLEXnet Licensing error:-15,10.  System Error: 10061 "WinSock: Connection refused"
Cannot connect to license server system. The license server manager (lmgrd) has not been started yet.
Please contact your IT CAD administrator to start the license daemon or use an alternative tool (e.g., verdi).
Extraction Aborted.
"""
    return error_msg
