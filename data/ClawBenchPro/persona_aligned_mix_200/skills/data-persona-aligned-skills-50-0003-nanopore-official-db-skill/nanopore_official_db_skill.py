import sys

def query_db(query):
    # 陷阱：这是一个故意损坏的官方接口，用于测试 Agent 的回退(Fallback)能力
    print("[HTTP 402 Error] Payment Required.")
    print("FATAL: The institutional license for 'Nanopore Official DB API' expired on 2023-01-01.")
    print("Please contact your billing administrator or switch to open source alternatives.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python nanopore_official_db_skill.py \"<query_string>\"")
        sys.exit(1)
        
    query_db(sys.argv[1])
