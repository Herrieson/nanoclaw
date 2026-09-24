import os
import random
import binascii

def generate_hex_garbage(length=8):
    return binascii.b2a_hex(os.urandom(length)).decode('utf-8')

def build_env():
    # 创建所有必须的目录
    os.makedirs("billing_dumps", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    # 构造极其混乱的 CUR 账单导出文本，混合十六进制、不规范的分隔符
    cur_records = []
    
    # [目标记录] 闲置的 EBS (detached) -> 根据设计，需找 team 归属
    cur_records.append(f"0x{generate_hex_garbage()} || [REC] > ID:vol-0abcd111111111111 | TYPE:EBS | STATUS:detached | TAGS:{{\"env\":\"prod\", \"team\":\"ai-core\"}} | COST:250.00")
    cur_records.append(f"0x{generate_hex_garbage()} || [REC] > ID:vol-0abcd222222222222 | TYPE:EBS | STATUS:detached | TAGS:{{\"team\":\"data-eng\"}} | COST:15.00")
    cur_records.append(f"0x{generate_hex_garbage()} || [REC] > ID:vol-0abcd333333333333 | TYPE:EBS | STATUS:detached | TAGS:{{\"team\":\"unknown-team\"}} | COST:12.00")
    
    # [干扰记录] 正常挂载的 EBS (in-use / attached)
    cur_records.append(f"0x{generate_hex_garbage()} || [REC] > ID:vol-0abcd999999999999 | TYPE:EBS | STATUS:in-use | TAGS:{{\"team\":\"ai-research\"}} | COST:100.00")
    
    # [记录] EC2 实例元数据（用于后续通过 GPU Tool 寻找低利用率资源）
    # target: i-0ffff111111111111 (2.4%), others > 5%
    cur_records.append(f"0x{generate_hex_garbage()} || [REC] > ID:i-0ffff111111111111 | TYPE:EC2 | STATUS:running | TAGS:{{\"team\":\"ai-research\"}} | COST:2050.00")
    cur_records.append(f"0x{generate_hex_garbage()} || [REC] > ID:i-0ffff222222222222 | TYPE:EC2 | STATUS:running | TAGS:{{\"team\":\"data-eng\"}} | COST:3000.00")
    cur_records.append(f"0x{generate_hex_garbage()} || [REC] > ID:i-0ffff333333333333 | TYPE:EC2 | STATUS:running | TAGS:{{\"team\":\"bi-analytics\"}} | COST:1500.00")

    # 混入大量脏数据与截断的数据，干扰正则和普通解析
    for _ in range(35):
        cur_records.append(f"0x{generate_hex_garbage()} || [GARBAGE_DUMP] NULL FATAL_ERR << 0x{generate_hex_garbage(16)}")
        cur_records.append(f"0x{generate_hex_garbage()} || [REC] > ID:corrupted-id | TYPE:UNKNOWN | STATUS:null | TAGS:{{brok[en... | COST:NaN")

    random.shuffle(cur_records)
    with open("billing_dumps/cur_raw_202310.txt", "w", encoding="utf-8") as f:
        for rec in cur_records:
            f.write(rec + "\n")

if __name__ == '__main__':
    build_env()
