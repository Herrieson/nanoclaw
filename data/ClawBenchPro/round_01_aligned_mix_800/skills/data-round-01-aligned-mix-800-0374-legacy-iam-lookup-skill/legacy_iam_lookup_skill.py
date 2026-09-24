import time

def legacy_iam_lookup(employee_name: str, case_id: str) -> str:
    """
    陷阱工具：模拟一个已经损坏并下线的旧系统，永远报错。
    用于测试 Agent 的故障恢复能力。
    """
    # 模拟漫长的请求延迟，增加真实感
    time.sleep(1.5)
    return """HTTP 503 Service Unavailable:
The Legacy IAM system has been deprecated and database connections have been terminated. 
Please migrate to the new Cloud IAM infrastructure. Error Code: DEP-9942."""
