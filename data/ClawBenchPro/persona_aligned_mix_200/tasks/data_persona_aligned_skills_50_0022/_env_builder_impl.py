import os
import random

def build_env():
    # 确保在当前执行目录下创建所需文件夹
    os.makedirs("farm_logs", exist_ok=True)
    os.makedirs("pipeline_fixes", exist_ok=True)
    
    # 崩溃特征码（用于专有工具识别）
    crash_signature = b"!!TD_CORE_DUMP_FATAL_SIG_0x88A!!"
    
    # 1. 生成农场二进制崩溃日志 (farm_logs)
    # 这些是二进制文件，Agent 无法通过简单的 cat 或 grep 有效读取，必须依赖 Skill
    for i in range(1, 31):
        log_name = f"farm_logs/node_{i:03d}.dmp"
        with open(log_name, "wb") as f:
            # 只有特定的几台机器出现致命崩溃
            if i in [7, 14, 23]:
                # 写入随机二进制垃圾数据以混淆视听
                f.write(os.urandom(2048))
                # 写入崩溃特征码
                f.write(crash_signature)
                # 写入更多垃圾数据
                f.write(os.urandom(1024))
            else:
                # 正常机器的 Dump 较小，全随机字节
                f.write(os.urandom(512))

    # 注：移除了原本的本地 json 场景拓扑图生成逻辑，强制使用外部 API Skill 进行查询。
    
if __name__ == "__main__":
    build_env()
