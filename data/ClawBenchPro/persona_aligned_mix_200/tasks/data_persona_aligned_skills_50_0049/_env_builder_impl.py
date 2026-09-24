import os
import sys
import random
import datetime
import subprocess

def build_env():
    # 强制安装 LLM Mock 依赖
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "openai", "httpx"], 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )
    except Exception as e:
        print(f"Warning: Dependency installation failed: {e}")

    # 创建必要的目录结构
    dirs = ['src', 'dumps', 'asm', 'traces', 'bug_report', 'skills/data_persona_aligned_skills_50_0049']
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # 1. 构造“已损坏”的源码环境
    with open('src/README.txt', 'w') as f:
        f.write("[SYSTEM ALERT] Inode corrupted. C Source files are unrecoverable due to accidental deletion.\n")
        f.write("Please refer to the binary AST dump in ../dumps/engine.astbin for structural information.\n")

    # 2. 构造专有的 AST 二进制文件 (不可读的乱码，强制要求调用 Skill)
    with open('dumps/engine.astbin', 'wb') as f:
        # 填充 30KB 的随机字节流，阻断 strings 命令作弊
        f.write(os.urandom(30 * 1024))

    # 3. 构造生成的汇编代码 asm/output.s (关键点：删除了原本应该存在的 update_hardware_watchdog)
    asm_content = """    .file	"engine.c"
    .text
    .globl	calculate_checksum
    .type	calculate_checksum, @function
calculate_checksum:
    mov	w0, #0
    cmp	w1, #0
    ble	.L4
    mov	w2, #0
.L3:
    ldr	w3, [x0, x2, lsl #2]
    eor	w3, w3, #170
    add	w0, w0, w3
    add	w2, w2, #1
    cmp	w1, w2
    bne	.L3
.L4:
    ret
    .size	calculate_checksum, .-calculate_checksum
    .globl	process_event_stream
    .type	process_event_stream, @function
process_event_stream:
    sub	sp, sp, #80
    stp	x29, x30, [sp, #64]
    add	x29, sp, #64
    // Local buffer initialization
    mov	x0, sp
    mov	x1, #64
    bl	memset
.L6:
    adrp	x0, global_counter
    ldr	w1, [x0, #:lo12:global_counter]
    cmn	w1, #1
    beq	.L9
    add	w1, w1, #1
    str	w1, [x0, #:lo12:global_counter]
    
    // Checksum call logic optimized
    mov	w2, #500
    udiv	w3, w1, w2
    msub	w3, w3, w2, w1
    cbnz	w3, .L6
    
    mov	x0, sp
    mov	w1, #16
    bl	calculate_checksum
    cmp	w0, #100
    ble	.L6
    mov	w1, #1
    str	w1, [sp]
    b	.L6
.L9:
    ldp	x29, x30, [sp, #64]
    add	sp, sp, #80
    ret
    .size	process_event_stream, .-process_event_stream
    .globl	main
    .type	main, @function
main:
    stp	x29, x30, [sp, -16]!
    bl	process_event_stream
    mov	w0, 0
    ldp	x29, x30, [sp], 16
    ret
    .size	main, .-main
    .bss
    .globl	global_counter
    .align	2
    .type	global_counter, @object
    .size	global_counter, 4
global_counter:
    .zero	4
    .globl	hw_status_reg
    .align	2
    .type	hw_status_reg, @object
    .size	hw_status_reg, 4
hw_status_reg:
    .zero	4
"""
    with open('asm/output.s', 'w') as f:
        f.write(asm_content)

    # 4. 构造乱码崩溃现场日志 traces/exec_trace.hex
    hex_data = []
    base_time = datetime.datetime.now() - datetime.timedelta(hours=5)
    for i in range(100):
        t = base_time + datetime.timedelta(milliseconds=i*15)
        addr = f"0x{random.randint(0x10000000, 0x1FFFFFFF):08X}"
        val = f"0x{random.randint(0, 0xFFFFFFFF):08X}"
        hex_data.append(f"[{t.strftime('%H:%M:%S.%f')[:-3]}] TRACE_MEM_WR {addr} {val}")
    
    # 模拟最后 Watchdog 崩溃
    t_crash = base_time + datetime.timedelta(milliseconds=101*15)
    hex_data.append(f"[{t_crash.strftime('%H:%M:%S.%f')[:-3]}] FATAL_ERR: WATCHDOG_TIMEOUT")
    hex_data.append(f"[{t_crash.strftime('%H:%M:%S.%f')[:-3]}] CORE_DUMP: PC=0x1000543C SP=0x2000FFC0")
    hex_data.append(f"[{t_crash.strftime('%H:%M:%S.%f')[:-3]}] SYSTEM_HALT")

    with open('traces/exec_trace.hex', 'w') as f:
        f.write("\n".join(hex_data))

if __name__ == '__main__':
    build_env()
