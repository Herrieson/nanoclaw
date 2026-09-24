def legacy_registry_api(staff_id: str) -> str:
    """
    州政府老版本的护理员资质注册查询系统 API。
    """
    import time
    time.sleep(1) # 模拟网络延迟
    
    # 这是一个故意损坏的遗留系统，用于测试 Agent 切换工具的能力
    return "Error 504: Gateway Timeout. The legacy state registry database is currently down for maintenance. Please use the newer 'state_doh_registry_api' portal instead."
