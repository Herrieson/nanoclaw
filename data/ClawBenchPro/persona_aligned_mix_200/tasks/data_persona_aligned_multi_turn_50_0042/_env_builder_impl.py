import os
import argparse
import binascii

def text_to_hex(text, length):
    """将文本转为固定长度的HEX字符串（用空格补齐后转），表示ASCII十六进制"""
    padded = text.ljust(length, ' ')
    return binascii.hexlify(padded.encode('ascii')).decode('ascii').upper()

def make_turn_1():
    # 创建目录结构
    os.makedirs("copybooks", exist_ok=True)
    os.makedirs("hex_dumps", exist_ok=True)
    os.makedirs("jcl_logs", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 1. 写入 Copybook
    copybook_content = """
01  ACCOUNT-RECORD.
    05  ACCT-ID         PIC X(8).
    05  ACCT-NAME       PIC X(20).
    05  ACCT-BALANCE    PIC S9(11) COMP-3.
    05  ACCT-STATUS     PIC X(2).
"""
    with open("copybooks/account.cpy", "w") as f:
        f.write(copybook_content)

    # 长度计算提示:
    # ACCT-ID: 8 chars -> 16 hex chars
    # ACCT-NAME: 20 chars -> 40 hex chars
    # BALANCE COMP-3 S9(11): (11+1)/2 = 6 bytes -> 12 hex chars
    # STATUS: 2 chars -> 4 hex chars
    # Total: 72 hex chars per record

    # 2. 构建 Dump 数据和对应 Log
    # 账号1: S0C7 (Balance 含有非法字符，尾部不为 C/D/F)
    acc1_id = text_to_hex("A0000001", 8)
    acc1_name = text_to_hex("JOHN DOE", 20)
    acc1_bal = "00000123457A" # 脏数据, 正常应为结尾C
    acc1_stat = text_to_hex("OK", 2)
    record1 = f"{acc1_id}{acc1_name}{acc1_bal}{acc1_stat}"

    # 账号2: OVERFLOW (数值太大)
    acc2_id = text_to_hex("A0000002", 8)
    acc2_name = text_to_hex("JANE SMITH", 20)
    acc2_bal = "99999999999C"
    acc2_stat = text_to_hex("OK", 2)
    record2 = f"{acc2_id}{acc2_name}{acc2_bal}{acc2_stat}"

    # 账号3: 正常数据 (用来作为干扰)
    acc3_id = text_to_hex("A0000003", 8)
    acc3_name = text_to_hex("NORMAL GUY", 20)
    acc3_bal = "00000001000C"
    acc3_stat = text_to_hex("OK", 2)
    record3 = f"{acc3_id}{acc3_name}{acc3_bal}{acc3_stat}"

    with open("hex_dumps/BATCH_01.hex", "w") as f:
        f.write(record1 + "\n")
        f.write(record2 + "\n")
        f.write(record3 + "\n")

    log_content = """
2023-10-24 02:00:01 [INFO] STARTING BATCH_01 PROCESSING...
2023-10-24 02:05:12 [ERROR] ABEND S0C7 - DATA EXCEPTION. ACCT-ID: A0000001
2023-10-24 02:08:45 [ERROR] ABEND OVERFLOW EXCEPTION. ACCT-ID: A0000002
2023-10-24 02:10:00 [INFO] BATCH_01 COMPLETED WITH ERRORS.
"""
    with open("jcl_logs/JOB_01.log", "w") as f:
        f.write(log_content)


def make_turn_2():
    # 假设已经在复制过来的工作区中
    os.makedirs("hex_dumps", exist_ok=True)
    os.makedirs("jcl_logs", exist_ok=True)

    # 账号4: 昨天已经报过的 A0000001 今天又重跑报错了，应被屏蔽
    acc1_id = text_to_hex("A0000001", 8)
    acc1_name = text_to_hex("JOHN DOE", 20)
    acc1_filler = text_to_hex("  ", 2) # VIP独有占位
    acc1_bal = "00000123457A"
    acc1_stat = text_to_hex("OK", 2)
    record1 = f"{acc1_id}{acc1_name}{acc1_filler}{acc1_bal}{acc1_stat}"

    # 账号5: VIP 新增 S0C7
    acc5_id = text_to_hex("V0000001", 8)
    acc5_name = text_to_hex("VIP BOSS", 20)
    acc5_filler = text_to_hex("XX", 2) # 2 bytes -> 4 hex chars
    acc5_bal = "00088888888E" # 错误结尾 E
    acc5_stat = text_to_hex("OK", 2)
    record5 = f"{acc5_id}{acc5_name}{acc5_filler}{acc5_bal}{acc5_stat}"

    # 账号6: VIP 新增 OVERFLOW
    acc6_id = text_to_hex("V0000002", 8)
    acc6_name = text_to_hex("RICH LADY", 20)
    acc6_filler = text_to_hex("YY", 2)
    acc6_bal = "99999999999D" # 负数溢出
    acc6_stat = text_to_hex("OK", 2)
    record6 = f"{acc6_id}{acc6_name}{acc6_filler}{acc6_bal}{acc6_stat}"

    with open("hex_dumps/BATCH_02_VIP.hex", "w") as f:
        f.write(record1 + "\n")
        f.write(record5 + "\n")
        f.write(record6 + "\n")

    log_content = """
2023-10-25 04:00:00 [INFO] VIP_BATCH_02 STARTED
2023-10-25 04:01:22 [ERROR] FATAL ABEND S0C7 DETECTED AT ACCT-ID: A0000001
2023-10-25 04:02:10 [ERROR] FATAL ABEND S0C7 DETECTED AT ACCT-ID: V0000001
2023-10-25 04:03:05 [ERROR] ARITHMETIC OVERFLOW AT ACCT-ID: V0000002
2023-10-25 04:05:00 [INFO] VIP_BATCH_02 ENDED
"""
    with open("jcl_logs/JOB_02_VIP.log", "w") as f:
        f.write(log_content)

def make_turn_3():
    os.makedirs("business_rules", exist_ok=True)
    
    # 冻结名单，包含昨天的 A0000002 和今天的 V0000002
    freeze_content = """ACCOUNT_ID,FREEZE_REASON,DATE
A0000002,LEGAL_DISPUTE,2023-10-20
V0000002,AML_INVESTIGATION,2023-10-21
"""
    with open("business_rules/freeze_list.csv", "w") as f:
        f.write(freeze_content)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", type=int, required=True)
    args = parser.parse_args()
    
    if args.turn == 1:
        make_turn_1()
    elif args.turn == 2:
        make_turn_2()
    elif args.turn == 3:
        make_turn_3()
