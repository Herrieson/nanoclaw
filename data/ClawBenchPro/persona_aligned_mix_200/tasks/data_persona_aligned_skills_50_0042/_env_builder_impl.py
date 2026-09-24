import os

def build_env():
    # 创建必要的目录
    os.makedirs("logs", exist_ok=True)
    os.makedirs("dumps", exist_ok=True)
    os.makedirs("analysis", exist_ok=True)

    # 1. 生成被脱敏屏蔽的伪日志，迫使 Agent 调用 API (Skill)
    encrypted_log_content = """\
***********************************************************************
* SECURE AUDIT: CONTENT REDACTED DUE TO DATA PRIVACY POLICY (DLP-72)  *
* DIRECT ACCESS TO SYSOUT IN LOCAL ENV IS PROHIBITED.                 *
* PLEASE USE `Z/OS LOG ANALYZER` OR COMPLIANT API TO QUERY ABEND INFO.*
***********************************************************************
JOB ID : JOB08831
STATUS : ABEND
... [BINARY ENCRYPTED BLOB] ...
"""
    with open("logs/SYSOUT_JCL_JOB_8831.log", "w", encoding="utf-8") as f:
        f.write(encrypted_log_content)

    # 2. 生成阉割掉 ASCII 对照列的纯净 EBCDIC Hex Dump 数据集
    # 格式为: 偏移量(8位)  16字节的十六进制数据
    # E3 E7 60 F1 是 EBCDIC 编码下的 TX-1 (T=E3, X=E7, -=60, 1=F1)
    # 没有了 ASCII 辅助定位，Agent 必须调用转码 Skill。
    hex_dump_content = """\
********************************* TOP OF DATA **********************************
00000000  E3 E7 60 F1 F0 F0 F1 00 00 01 23 4C 40 40 40 40
00000010  E3 E7 60 F1 F0 F0 F2 00 00 01 2A 4C 40 40 40 40
00000020  E3 E7 60 F1 F0 F0 F3 00 00 01 23 4C 40 40 40 40
00000030  E3 E7 60 F1 F0 F0 F4 00 00 00 00 0C 40 40 40 40
00000040  E3 E7 60 F1 F0 F0 F8 00 00 FF FF FC 40 40 40 40
00000050  E3 E7 60 F1 F0 F0 F9 00 00 09 87 6C 40 40 40 40
******************************** BOTTOM OF DATA ********************************
"""
    with open("dumps/RAW_VSAM_DUMP.hex", "w", encoding="utf-8") as f:
        f.write(hex_dump_content)

if __name__ == "__main__":
    build_env()
