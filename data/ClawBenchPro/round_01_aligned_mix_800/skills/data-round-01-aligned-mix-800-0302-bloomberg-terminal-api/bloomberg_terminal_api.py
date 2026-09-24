import time

def query_bloomberg_commodity(commodity_ticker: str) -> str:
    """
    陷阱工具：模拟一个极其权威但当前无法使用的 API，测试 Agent 在面对环境故障时的处理能力。
    """
    # 假装进行了一次网络连接
    time.sleep(1.5)
    
    # 始终返回授权失败，促使 Agent 去寻找替代方案
    error_msg = (
        "Error 402: Payment Required. \n"
        "Message: Your organization's Bloomberg Terminal enterprise license has expired. "
        "Please contact your administrator to renew the subscription or use fallback API services."
    )
    return error_msg
