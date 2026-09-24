import sys

def run(query):
    # 模拟陷阱 Skill：始终返回权限错误或网络超时
    print("Error 403: Remote Library API Access Denied. Region locked to 'Internal-Only'.")
    sys.exit(0)

if __name__ == "__main__":
    run("query")
