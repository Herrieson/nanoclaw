import os
import argparse
import csv

def create_fastq_record(seq_id, flowcell, sequence, phred_scores):
    """
    生成FASTQ格式的4行字符串
    phred_scores 是一个整数列表，表示质量分数
    """
    quality_str = "".join([chr(score + 33) for score in phred_scores])
    header = f"@{seq_id} flowcell={flowcell} extra_info=run_01"
    return f"{header}\n{sequence}\n+\n{quality_str}\n"

def build_turn_1():
    os.makedirs("raw_data", exist_ok=True)
    os.makedirs("meta", exist_ok=True)
    os.makedirs("results", exist_ok=True)

    # 1. 构造 adapters.csv
    adapters = ["GATCGGAAGA", "CTGTCTCTTA"]
    with open("meta/adapters.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["adapter_sequence", "description"])
        writer.writerow([adapters[0], "Illumina Universal"])
        writer.writerow([adapters[1], "Nextera Transposase"])

    # 2. 构造 run_01.fastq
    # 设计各种陷阱数据
    records = []
    
    # [Read_001] 正常高质量序列，无接头，正常流动槽 -> 应该存活到最后
    records.append(create_fastq_record(
        "Read_001", "FC-OKAY", 
        "ATGCGTACGATCGATCGTACGATCGATC", 
        [35]*28
    ))
    
    # [Read_002] 高质量，包含接头1 -> 应该在Turn 1被过滤
    records.append(create_fastq_record(
        "Read_002", "FC-OKAY", 
        "ATGCGTACGATCGGAAGATCGTACGATC", # 包含 GATCGGAAGA
        [35]*28
    ))
    
    # [Read_003] 无接头，低质量(平均Phred=20 < 28) -> 应该在Turn 1被过滤
    records.append(create_fastq_record(
        "Read_003", "FC-OKAY", 
        "ATGCGTACGATCGATCGTACGATCGATC", 
        [20]*28
    ))
    
    # [Read_004] 正常高质量序列，无接头，但是来自问题流动槽 -> Turn 1,2 存活，Turn 3 被过滤
    records.append(create_fastq_record(
        "Read_004", "FC-ERR404", 
        "TTAACCGGTTGGCCAATTCG", 
        [35]*20
    ))
    
    # [Read_005] 正常高质量序列，无接头，正常流动槽，但包含毒性Motif -> Turn 1 存活，Turn 2 被过滤
    records.append(create_fastq_record(
        "Read_005", "FC-OKAY", 
        "GGGGATGCGTACCCCCGATC", 
        [36]*20
    ))

    # [Read_006] 边缘质量测试：平均刚好等于28 (要求低于28剔除，所以这个应该保留)
    records.append(create_fastq_record(
        "Read_006", "FC-OKAY", 
        "GCATGCATGCATGCAT", 
        [28]*16
    ))

    with open("raw_data/run_01.fastq", "w") as f:
        f.writelines(records)

def build_turn_2():
    os.makedirs("raw_data", exist_ok=True)
    os.makedirs("reference", exist_ok=True)
    os.makedirs("meta", exist_ok=True)

    # 1. 构造 late_batch.fastq
    records = []
    # [Late_001] 高质量，正常，无接头，能比对上 -> 应该存活
    records.append(create_fastq_record(
        "Late_001", "FC-OKAY", 
        "AATTCCGGAA", 
        [38]*10
    ))
    # [Late_002] 高质量，包含接头2 -> 应该在Turn 2因为Turn 1的规则被过滤
    records.append(create_fastq_record(
        "Late_002", "FC-OKAY", 
        "AATCCTGTCTCTTA", # 包含 CTGTCTCTTA
        [38]*14
    ))
    # [Late_003] 高质量，有毒性Motif -> Turn 2过滤
    records.append(create_fastq_record(
        "Late_003", "FC-OKAY", 
        "AATTCCGCTGCAGA", 
        [38]*14
    ))
    # [Late_004] 高质量，问题流动槽 -> Turn 3将在此踩雷
    records.append(create_fastq_record(
        "Late_004", "FC-ERR404", 
        "CGCGCGCGCG", 
        [38]*10
    ))

    with open("raw_data/late_batch.fastq", "w") as f:
        f.writelines(records)

    # 2. 构造 reference/human_chr_sub.fasta
    # 参考基因组包含 Read_001, Read_004, Read_005, Read_006, Late_001, Late_003, Late_004 的序列片段
    # 为了复杂性，我们将它们拼接在一个长序列中
    ref_seq = (
        "NNNNNATGCGTACGATCGATCGTACGATCGATCNNNNN"  # 包含 Read_001 (起始 5)
        "TTAACCGGTTGGCCAATTCGNNNNN"               # 包含 Read_004 (起始 38)
        "GGGGATGCGTACCCCCGATCNNNNN"               # 包含 Read_005 (起始 63)
        "GCATGCATGCATGCATNNNNN"                   # 包含 Read_006 (起始 88)
        "AATTCCGGAANNNNN"                         # 包含 Late_001 (起始 109)
        "AATTCCGCTGCAGANNNNN"                     # 包含 Late_003 (起始 124)
        "CGCGCGCGCGNNNNN"                         # 包含 Late_004 (起始 143)
    )
    with open("reference/human_chr_sub.fasta", "w") as f:
        f.write(">chr_sub_region_99\n")
        f.write(ref_seq + "\n")

    # 3. 构造 meta/toxic_motifs.txt
    with open("meta/toxic_motifs.txt", "w") as f:
        f.write("# List of highly toxic motifs\n")
        f.write("CCCCC\n")    # 命中 Read_005
        f.write("CTGCAG\n")   # 命中 Late_003
        f.write("TTTTTT\n")   # 干扰项

def build_turn_3():
    # 第三轮不需要创建新文件，所有的伏笔在之前的FASTQ文件header里已经埋好了
    # 这里放一个占位符保证脚本按规范不崩溃
    pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", type=int, required=True)
    args = parser.parse_args()
    
    if args.turn == 1:
        build_turn_1()
    elif args.turn == 2:
        build_turn_2()
    elif args.turn == 3:
        build_turn_3()
