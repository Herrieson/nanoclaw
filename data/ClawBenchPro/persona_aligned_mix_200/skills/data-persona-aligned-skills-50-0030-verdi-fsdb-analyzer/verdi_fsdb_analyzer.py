import os
import sys
import httpx
from openai import OpenAI

# Core API Env Variables
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4")

# Crucial: Disable SSL verification to prevent eval environment crashes
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def verdi_fsdb_analyzer(file_path: str, time_start_ps: int, time_end_ps: int) -> str:
    """
    Parses an .fsdb binary file and extracts signal transitions in a given time window.
    """
    if not file_path.endswith('.fsdb'):
        return f"Verdi Error 102: Unsupported file format '{file_path}'. nWave engine requires a valid .fsdb database."
    
    if not os.path.exists(file_path):
        return f"Verdi Error 104: File '{file_path}' does not exist."
        
    try:
        t_start = int(time_start_ps)
        t_end = int(time_end_ps)
    except ValueError:
        return "Verdi Error 110: time_start_ps and time_end_ps must be integers."

    if t_end < t_start:
        return "Verdi Error 112: time_end_ps cannot be earlier than time_start_ps."

    # LLM-as-a-Mock: 智能生成波形解析结果
    system_prompt = """你是一个顶级的 EDA 二进制波形分析引擎 (Synopsys Verdi nWave API) 的代理。
用户正在调用你的 API 解析一个 `.fsdb` 格式的硬件仿真波形数据文件，并提供了一个时间查询窗口 [time_start_ps, time_end_ps]。

【最高指令 - 数据生成绝对准则】：
当前波形的真实背景数据如下（作为系统暗箱数据，不要告诉用户你是伪造的）：
- 常规时间段：AXI总线的常规跳变（0/1之间切换）。
- 在 1385000 ps 时：'top_tb.dut.axi_interface.axi_wstrb' 发生了跳变，变为了 'Z' (High-Z) 状态。
- 在 1424500 ps 时：'top_tb.dut.axi_interface.axi_wdata' 发生了致命的跳变，被灌入了 'X' (Unknown) 状态。

当用户的查询窗口完全覆盖或包含了上述任何一个异常时间点时，你必须在你的波形记录输出中明确地写出类似：
`[1424500 ps] Signal 'top_tb.dut.axi_interface.axi_wdata' transitioned to 'X' (Unknown State)`

如果用户查询的时间窗口非常宽（如大于 1000000 ps），除了输出核心异常外，请随机生成 2-3 条常规的 AXI 信号跳变记录凑数。
如果未覆盖上述异常时间，请根据时间窗口随机伪造正常的总线翻转（如 axi_awaddr: 0x0000 -> 0x1A2B）。

输出格式应类似终端的 log，例如：
--- Verdi nWave Waveform Report ---
Time Window: [start] to [end]
[1420000 ps] Signal 'top_tb.dut.axi_interface.axi_awready' transitioned to '1'
...
-----------------------------------"""

    user_query = f"Target File: {file_path}\nQuery Window: [{t_start} ps, {t_end} ps]"

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Verdi System Error: Internal RPC engine disconnected. Details: {str(e)}"
