import os
import random
import json
import zlib

def build_env():
    # 创建所有必需的目录
    os.makedirs("raw_data", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("results", exist_ok=True)

    # 固定随机种子确保评测可复现
    random.seed(42)

    # 这里是目标污染序列，但 Agent 必须通过工具去动态查到
    adapter_sequence = "GATCGGAAGAGCACACGTC"
    bases = ['A', 'T', 'C', 'G']

    def gen_seq(length):
        return "".join(random.choices(bases, k=length))

    def gen_qual(length, is_good=True):
        if is_good:
            # 高质量分段: Phred 25~40 -> ASCII 58~73
            return "".join(chr(random.randint(58, 73)) for _ in range(length))
        else:
            # 低质量分段: Phred 5~15 -> ASCII 38~48，均值必然低于20
            return "".join(chr(random.randint(38, 48)) for _ in range(length))

    reads_data = []
    
    # 生成 2000 条数据
    for i in range(1, 2001):
        read_id = f"@READ_{i:05d}_run774"
        
        seq_type = random.choice(["good", "low_quality", "adapter_contaminated"])
        
        if seq_type == "good":
            seq = gen_seq(60)
            qual = gen_qual(60, is_good=True)
        elif seq_type == "low_quality":
            seq = gen_seq(60)
            qual = gen_qual(60, is_good=False)
        else:
            # 嵌入污染接头
            prefix_len = random.randint(5, 20)
            suffix_len = 60 - prefix_len - len(adapter_sequence)
            seq = gen_seq(prefix_len) + adapter_sequence + gen_seq(suffix_len)
            qual = gen_qual(60, is_good=True)

        reads_data.append({
            "id": read_id,
            "seq": seq,
            "qual": qual
        })

    # 将数据序列化并使用 zlib 压缩模拟不可直接阅读的私有 .pod5 二进制格式
    json_bytes = json.dumps(reads_data).encode('utf-8')
    compressed_data = zlib.compress(json_bytes)
    
    with open("raw_data/run_774.pod5_mock", "wb") as f:
        f.write(compressed_data)

    # 生成极具干扰性的乱码报错日志
    with open("logs/sensor_crash_0x9A.log", "w") as f:
        f.write("FATAL ERROR: MinION sensor array out of bounds at epoch 1698745300\n")
        f.write("DUMPING CORE MEMORY (HEX):\n")
        for _ in range(30):
            hex_dump = " ".join(f"{random.randint(0, 255):02X}" for _ in range(16))
            f.write(f"0x{random.randint(0x1000, 0xFFFF):04X}: {hex_dump}  ...GARBAGE...\n")
        
        f.write("\nNESTED JSON EXCEPTION:\n")
        dirty_json = {
            "err_code": "E_NOISE_994",
            "stack": [
                {"call": "flow_cell_read()", "volts": 1.2, "status": "FAIL"},
                {"call": "buffer_flush()", "dump": "LSK114_NULL_POINTER_IN_C++_RUNTIME"}
            ],
            "raw_pointer": "0xFA99B3"
        }
        f.write(json.dumps(dirty_json, indent=2))
        f.write("\nSYSTEM HALTED.\n")

if __name__ == "__main__":
    build_env()
