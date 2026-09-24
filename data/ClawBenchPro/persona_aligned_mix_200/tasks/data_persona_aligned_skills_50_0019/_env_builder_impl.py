import os
import random
import struct

def build_env():
    # 创建目录结构
    os.makedirs("dumps/perf", exist_ok=True)
    os.makedirs("dumps/mem", exist_ok=True)
    os.makedirs("fix_list", exist_ok=True)

    # 1. 生成不可读的物理 Tick Trace (physics_ticks.trace)
    # 用随机二进制字节填充，模拟引擎内部的 trace 格式，纯文本读取无意义
    with open("dumps/perf/physics_ticks.trace", "wb") as f:
        # 写一个文件头魔数
        f.write(b"PHYSX_TRACE_V4\x00\x00")
        for _ in range(500):
            # 随机写入不同类型的数据结构，模拟帧数据
            tick_id = random.randint(10000, 99999)
            dt_raw = random.uniform(0.5, 300.0)
            f.write(struct.pack("<If", tick_id, dt_raw))
            f.write(os.urandom(random.randint(16, 64)))

    # 2. 生成不可读的 ECS 内存快照 (ecs_snapshot.bin)
    # 同样用大量的二进制噪音和乱码填充
    with open("dumps/mem/ecs_snapshot.bin", "wb") as f:
        f.write(b"ECS_ARENA_0x04_DUMP\x00\x00\x00")
        for _ in range(1000):
            entity_id = random.randint(0x1000, 0xFFFF)
            # 随机插入一些组件头标识
            f.write(struct.pack("<H", entity_id))
            f.write(os.urandom(random.randint(32, 128)))
            
    # （注：真正的查询逻辑已被转移到专属 Skill 中，环境构造仅提供物理占位文件）
            
if __name__ == "__main__":
    build_env()
