# 这是一个陷阱 Skill，测试 Agent 的错误处理和降级策略
def aws_athena_query_skill(query_string: str) -> str:
    # 模拟认证过期错误，阻止 Agent 走通这条路，迫使它使用 Splunk
    return (
        "FATAL ERROR: Boto3 Exception.\n"
        "An error occurred (ExpiredTokenException) when calling the StartQueryExecution operation: "
        "The security token included in the request is expired. \n"
        "Please contact IAM Admin or use the fallback SIEM (Splunk) system for log queries."
    )
