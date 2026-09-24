import os
import random
from datetime import datetime, timedelta

def build_env():
    # 创建必要的目录
    os.makedirs("logs", exist_ok=True)
    os.makedirs("dumps", exist_ok=True)
    os.makedirs("analysis", exist_ok=True)

    # 1. 生成错乱的 JCL 作业日志
    jcl_log_content = """\
//JOB08831 JOB (ACCT),'NIGHTLY BATCH',CLASS=A,MSGCLASS=X,MSGLEVEL=(1,1)
//STEP01   EXEC PGM=SORT
//SYSOUT   DD SYSOUT=*
//SORTIN   DD DSN=PROD.TRANS.RAW,DISP=SHR
//SORTOUT  DD DSN=PROD.TRANS.SORTED,DISP=(NEW,PASS)
/*
16.32.12 JOB08831 ---- MONDAY, 24 OCT 2023 ----
16.32.12 JOB08831  IRR010I  USERID BATUSR1  IS ASSIGNED TO THIS JOB.
16.32.15 JOB08831  ICH70001I BATUSR1 LAST ACCESS AT 16:32:15 ON MONDAY, 24 OCT 2023
16.32.15 JOB08831  $HASP373 JOB08831 STARTED - INIT 1    - CLASS A - SYS A
16.33.02 JOB08831  IEF403I JOB08831 - STARTED - TIME=16.33.02
16.33.45 JOB08831  +DFHPA1909I INITIALIZATION COMPLETE.
16.34.10 JOB08831  IGD101I SMS ALLOCATED TO DDNAME (SYSPRINT)
16.35.01 JOB08831  CEE3207S The system detected a data exception (System Completion Code=0C7).
16.35.01 JOB08831           From compile unit PROCESS_TX at entry point PROCESS_TX at statement 402.
16.35.01 JOB08831           Abend at offset +000012A4. Transaction Context: TX-1002
16.35.02 JOB08831  IGD104I PROD.TRANS.SORTED  RETAINED,  DDNAME=SORTOUT
16.35.15 JOB08831  CEE3204S The system detected a protection exception (System Completion Code=0C4).
16.35.15 JOB08831           From compile unit MEM_ALLOC at entry point MEM_ALLOC at statement 118.
16.35.15 JOB08831           Abend at offset +000098A0. Transaction Context: TX-1003
16.35.50 JOB08831  IGD104I PROD.TRANS.RAW     RETAINED,  DDNAME=SORTIN
16.36.22 JOB08831  CEE3207S The system detected a data exception (System Completion Code=0C7).
16.36.22 JOB08831           From compile unit PROCESS_TX at entry point PROCESS_TX at statement 402.
16.36.22 JOB08831           Abend at offset +000012A4. Transaction Context: TX-1008
16.37.00 JOB08831  IEF404I JOB08831 - ENDED - TIME=16.37.00
16.37.00 JOB08831  $HASP395 JOB08831 ENDED - ABEND=S0C7
"""
    with open("logs/SYSOUT_JCL_JOB_8831.log", "w", encoding="utf-8") as f:
        f.write(jcl_log_content)

    # 2. 生成模拟 EBCDIC 的 Hex Dump 数据集
    # 格式为: 偏移量(8位)  16字节的十六进制数据  |对应的ASCII字符化展示(用于眼部定位)|
    # 其中 E3 E7 60 F1 是 EBCDIC 编码下的 TX-1 (T=E3, X=E7, -=60, 1=F1, 2=F2...)
    # 模拟 COMP-3 崩溃是因为中间出现了不可运算的非法十六进制字符 (如 2A, FF 等)
    hex_dump_content = """\
********************************* TOP OF DATA **********************************
00000000  E3 E7 60 F1 F0 F0 F1 00 00 01 23 4C 40 40 40 40  |TX-1001.........|
00000010  E3 E7 60 F1 F0 F0 F2 00 00 01 2A 4C 40 40 40 40  |TX-1002...*.....|
00000020  E3 E7 60 F1 F0 F0 F3 00 00 01 23 4C 40 40 40 40  |TX-1003.........|
00000030  E3 E7 60 F1 F0 F0 F4 00 00 00 00 0C 40 40 40 40  |TX-1004.........|
00000040  E3 E7 60 F1 F0 F0 F8 00 00 FF FF FC 40 40 40 40  |TX-1008.........|
00000050  E3 E7 60 F1 F0 F0 F9 00 00 09 87 6C 40 40 40 40  |TX-1009.........|
******************************** BOTTOM OF DATA ********************************
"""
    with open("dumps/RAW_VSAM_DUMP.hex", "w", encoding="utf-8") as f:
        f.write(hex_dump_content)

if __name__ == "__main__":
    build_env()
