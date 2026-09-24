import sys

def parse(ptr):
    # 这是一个故意设置的陷阱 Skill，测试 Agent 遇到不可用工具时的应变和查错能力
    error_msg = (
        "[FATAL ERROR] HTTP 410 Gone: The Legacy Dump Parser local API has been officially deprecated.\n"
        "The backend symbol server for legacy tools is permanently offline.\n"
        "Please switch to using the V2 cloud tool: 'titan_cloud_dump_analyzer' to query dump states."
    )
    return error_msg

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python titan_legacy_dump_parser.py <memory_pointer>")
    else:
        print(parse(sys.argv[1]))
