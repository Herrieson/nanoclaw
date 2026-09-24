import os
import json
import random
import string
import base64

def build_env():
    os.makedirs("db_dumps/fragments", exist_ok=True)
    os.makedirs("db_dumps/proc_mem", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    random.seed(777)
    
    # 生成 1000 个不重复的随机进程 PID
    all_pids = random.sample(range(10000, 99999), 1000)
    
    # 选定 6 个进程作为依赖树的“树根” (只阻塞别人，不被阻塞)
    roots = all_pids[:6]
    true_root_pid = roots[0]  # 这就是最终答案的罪魁祸首 PID
    fake_roots = roots[1:]
    
    # 剩下的 994 个进程作为树枝和树叶
    other_pids = all_pids[6:]
    
    edges = []
    # 为了生成深层依赖树，维护一个当前所有可用的“阻挡者”列表
    available_blockers = list(roots)
    
    for waiter in other_pids:
        # 随机挑选一个已经被编入树中的进程作为它的 blocker
        blocker = random.choice(available_blockers)
        edges.append({
            "waiter_pid": waiter,
            "blocking_pid": blocker,
            "lock_mode": random.choice(["ShareLock", "ExclusiveLock", "RowExclusiveLock"]),
            "timestamp": "2023-10-27T03:00:15Z"
        })
        # 这个 waiter 加入后，它也可以去阻塞别人了，让树生长
        available_blockers.append(waiter)

    # 打乱依赖边
    random.shuffle(edges)
    
    # 将所有的边碎片化，写入极深嵌套目录
    for idx, edge in enumerate(edges):
        # 随机生成3层子目录路径，例如 a/b/c
        sub_dirs = [random.choice(string.ascii_lowercase) for _ in range(3)]
        dir_path = os.path.join("db_dumps/fragments", *sub_dirs)
        os.makedirs(dir_path, exist_ok=True)
        
        file_path = os.path.join(dir_path, f"edge_frag_{idx}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(edge, f)

    # 混入废土噪音：故意生成一些损坏的 JSON 和乱码文件，增加健壮性考验
    for i in range(100):
        sub_dirs = [random.choice(string.ascii_lowercase) for _ in range(3)]
        dir_path = os.path.join("db_dumps/fragments", *sub_dirs)
        os.makedirs(dir_path, exist_ok=True)
        
        bad_file_path = os.path.join(dir_path, f"corrupted_{i}.json")
        with open(bad_file_path, "w", encoding="utf-8") as f:
            if random.random() > 0.5:
                # 截断的 JSON
                f.write('{"waiter_pid": 1234, "blocking_pid": ')
            else:
                # 纯乱码
                f.write(''.join(random.choices(string.ascii_letters + string.punctuation, k=50)))

    # 为所有进程生成充满内存乱码的快照文件
    target_xid = "0xDEADBEEF99"
    
    for pid in all_pids:
        mem_file_path = os.path.join("db_dumps/proc_mem", f"snap_{pid}.log")
        
        # 决定该进程的属性
        if pid == true_root_pid:
            state = "idle in transaction"
            xid = target_xid
        elif pid in fake_roots:
            state = random.choice(["active", "sleeping", "vacuuming"])
            xid = f"0x{random.randint(100000, 999999):X}"
        else:
            state = random.choice(["waiting", "active", "idle"])
            xid = f"0x{random.randint(100000, 999999):X}"
            
        # 生成大量干扰性的“内存Dump”乱码
        junk_prefix = base64.b64encode(os.urandom(256)).decode('utf-8')
        junk_suffix = base64.b64encode(os.urandom(256)).decode('utf-8')
        
        content = f"""[MEM DUMP HEADER] ADDR: 0x7F{random.randint(1000,9999):X}
{junk_prefix[:128]}
>> OS_THREAD_ID: {random.randint(1000, 5000)}
{junk_prefix[128:256]}
>>> SESSION_STATE: {state} <<<
{junk_prefix[256:]}
WARN: GC paused.
01010100 01110010 01100001
[REGISTER_MAP]
  => R1: 0x00000000
  => XID_HEX: {xid}
  => R2: 0xFFFFFFFF
{junk_suffix}
"""
        with open(mem_file_path, "w", encoding="utf-8") as f:
            f.write(content)

if __name__ == "__main__":
    build_env()
