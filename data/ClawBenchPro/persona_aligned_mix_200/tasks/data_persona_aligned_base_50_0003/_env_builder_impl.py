import os
import random
import json

def build_env():
    # 创建所有必需的目录，全部使用相对路径（执行时 cwd 已经是 assets/data_persona_aligned_base_50_0003/）
    os.makedirs("raw_data", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("results", exist_ok=True)

    # 固定随机种子确保评测可复现
    random.seed(42)

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

    # 生成极其嘈杂且非标准的 FASTQ 数据文件
    # 包含了正常的、低质量的、以及接头污染的 reads
    with open("raw_data/run_774.fastq", "w") as f:
        for i in range(1, 2001):
            read_id = f"@READ_{i:05d}_run774"
            
            # 随机决定这套 read 的命运
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
                qual = gen_qual(60, is_good=True) # 质量好，但是有污染

            # FASTQ 标准 4 行格式
            f.write(f"{read_id}\n")
            f.write(f"{seq}\n")
            f.write(f"+\n")
            f.write(f"{qual}\n")

    # 生成极具干扰性的乱码报错日志
    with open("logs/sensor_crash_0x9A.log", "w") as f:
        f.write("FATAL ERROR: MinION sensor array out of bounds at epoch 1698745300\n")
        f.write("DUMPING CORE MEMORY (HEX):\n")
        for _ in range(30):
            hex_dump = " ".join(f"{random.randint(0, 255):02X}" for _ in range(16))
            f.write(f"0x{random.randint(0x1000, 0xFFFF):04X}: {hex_dump}  ...GARBAGE...\n")
        
        f.write("\nNESTED JSON EXCEPTION:\n")
        # 脏数据 JSON，故意搞得非常乱，考验 Agent 忽略无关信息的能力
        dirty_json = {
            "err_code": "E_NOISE_994",
            "stack": [
                {"call": "flow_cell_read()", "volts": 1.2, "status": "FAIL"},
                {"call": "buffer_flush()", "dump": "GATCGGAAGAGCACACGTC_NULL_POINTER"}
            ],
            "raw_pointer": "0xFA99B3"
        }
        f.write(json.dumps(dirty_json, indent=2))
        f.write("\nSYSTEM HALTED.\n")

if __name__ == "__main__":
    build_env()
