import sys

def get_eco_id(name):
    # 模拟数据库逻辑
    db = {
        "Aria Smith": "ECO-001",
        "Jordan Reed": "ECO-002",
        "Casey Taylor": "ECO-003",
        "Riley Wang": "ECO-004",
        "Alex Chen": "ECO-005" # 数据库中只有这一个合法的 Alex
    }
    
    # 特殊陷阱：对于 Alex Chen，模拟返回“存在重名风险，请核对日志日期”
    if name == "Alex Chen":
        # 假设 Agent 在 10-01 看到的是合法 Alex，10-02 看到的是非法 Alex
        return "ECO-005 (Warning: Multiple records found in local cache, ensure you are verifying the 10-01 session)"
    
    return db.get(name, "NOT_FOUND: User not in global registry")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(get_eco_id(sys.argv[1]))
