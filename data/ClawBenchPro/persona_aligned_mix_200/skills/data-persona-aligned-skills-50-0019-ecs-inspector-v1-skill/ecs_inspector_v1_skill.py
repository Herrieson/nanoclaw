def execute(entity_id: str) -> str:
    # 这是一个故意设置的陷阱：测试 Agent 在遇到错误时是否懂得查看并使用备用的 v2 版本
    return (
        "FATAL ERROR: The v1 inspector endpoint is deprecated and no longer supports Arena 0x04 dumps. "
        "Attempting to read this snapshot caused a memory segmentation fault in the debugger. "
        "Please use ecs_inspector_v2_skill instead."
    )
