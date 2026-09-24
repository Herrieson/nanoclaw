import os
import random
import datetime

def build_env():
    # 创建必要的目录结构
    dirs = ['src', 'dumps', 'asm', 'traces', 'bug_report']
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # 1. 构造源码 src/engine.c
    c_code = """#include <stdint.h>

volatile uint32_t hw_status_reg = 0;
uint32_t global_counter = 0;

static void __attribute__((noinline)) update_hardware_watchdog(void) {
    // Critical state update, mistakenly evaluated as pure/dead by flawed DCE
    hw_status_reg = 0xDEADBEEF;
}

int calculate_checksum(int *data, int len) {
    int sum = 0;
    for(int i=0; i<len; ++i) {
        sum += data[i] ^ 0xAA;
    }
    return sum;
}

void process_event_stream(void) {
    int buffer[16] = {0};
    while(global_counter < 0xFFFFFFFF) {
        global_counter++;
        if (global_counter % 1000 == 0) {
            update_hardware_watchdog();
        }
        
        if (global_counter % 500 == 0) {
            int chk = calculate_checksum(buffer, 16);
            if (chk > 100) {
                buffer[0] = 1;
            }
        }
    }
}

int main() {
    process_event_stream();
    return 0;
}
"""
    with open('src/engine.c', 'w') as f:
        f.write(c_code)

    # 2. 构造 AST Dump 日志 (dumps/ast_dump.log)
    ast_content = """TranslationUnitDecl 0x55a9b9a9b008 <<invalid sloc>> <invalid sloc>
|-TypedefDecl 0x55a9b9a9b8a0 <<invalid sloc>> <invalid sloc> implicit __int128_t '__int128'
| `-BuiltinType 0x55a9b9a9b660 '__int128'
|-TypedefDecl 0x55a9b9a9b8d0 <<invalid sloc>> <invalid sloc> implicit __uint128_t 'unsigned __int128'
| `-BuiltinType 0x55a9b9a9b680 'unsigned __int128'
|-VarDecl 0x55a9b9ab0010 <src/engine.c:3:1, col:35> col:19 hw_status_reg 'volatile uint32_t':'volatile unsigned int' cinit
| `-IntegerLiteral 0x55a9b9ab0078 <col:35> 'int' 0
|-VarDecl 0x55a9b9ab00a8 <line:4:1, col:27> col:10 global_counter 'uint32_t':'unsigned int' cinit
| `-IntegerLiteral 0x55a9b9ab0110 <col:27> 'int' 0
|-FunctionDecl 0x55a9b9ab0220 <line:6:1, line:9:1> line:6:39 used update_hardware_watchdog 'void ()' static
| |-CompoundStmt 0x55a9b9ab03a8 <line:6:46, line:9:1>
| | `-BinaryOperator 0x55a9b9ab0388 <line:8:5, col:21> 'volatile uint32_t':'volatile unsigned int' '='
| |   |-DeclRefExpr 0x55a9b9ab0348 <col:5> 'volatile uint32_t':'volatile unsigned int' lvalue Var 0x55a9b9ab0010 'hw_status_reg' 'volatile uint32_t':'volatile unsigned int'
| |   `-ImplicitCastExpr 0x55a9b9ab0370 <col:21> 'volatile uint32_t':'volatile unsigned int' <IntegralCast>
| |     `-IntegerLiteral 0x55a9b9ab0328 <col:21> 'unsigned int' 3735928559
|-FunctionDecl 0x55a9b9ab0450 <line:11:1, line:17:1> line:11:5 used calculate_checksum 'int (int *, int)'
| |-ParmVarDecl 0x55a9b9ab03d0 <col:24, col:29> col:29 used data 'int *'
| |-ParmVarDecl 0x55a9b9ab0400 <col:35, col:39> col:39 used len 'int'
| `-CompoundStmt 0x55a9b9ab0810 <line:11:44, line:17:1>
|   |-DeclStmt 0x55a9b9ab0528 <line:12:5, col:16>
|   | `-VarDecl 0x55a9b9ab04f0 <col:5, col:15> col:9 used sum 'int' cinit
|   |   `-IntegerLiteral 0x55a9b9ab0518 <col:15> 'int' 0
|   |-ForStmt 0x55a9b9ab07c8 <line:13:5, line:15:5>
|   `-ReturnStmt 0x55a9b9ab0800 <line:16:5, col:12>
|     `-ImplicitCastExpr 0x55a9b9ab07e8 <col:12> 'int' <LValueToRValue>
|       `-DeclRefExpr 0x55a9b9ab07a8 <col:12> 'int' lvalue Var 0x55a9b9ab04f0 'sum' 'int'
|-FunctionDecl 0x55a9b9ab08b8 <line:19:1, line:33:1> line:19:6 used process_event_stream 'void ()'
| `-CompoundStmt 0x55a9b9ab0ee8 <line:19:33, line:33:1>
|   |-DeclStmt 0x55a9b9ab0a60 <line:20:5, col:25>
|   |-WhileStmt 0x55a9b9ab0ed0 <line:21:5, line:32:5>
|     |-BinaryOperator 0x55a9b9ab0af0 <line:21:11, col:28> 'int' '<'
|     `-CompoundStmt 0x55a9b9ab0eb8 <line:21:42, line:32:5>
|       |-UnaryOperator 0x55a9b9ab0b30 <line:22:9, col:23> 'uint32_t':'unsigned int' postfix '++'
|       |-IfStmt 0x55a9b9ab0c28 <line:23:9, line:25:9>
|       | |-BinaryOperator 0x55a9b9ab0bd8 <line:23:13, col:33> 'int' '=='
|       | | |-BinaryOperator 0x55a9b9ab0b90 <col:13, col:28> 'uint32_t':'unsigned int' '%'
|       | | | |-ImplicitCastExpr 0x55a9b9ab0b78 <col:13> 'uint32_t':'unsigned int' <LValueToRValue>
|       | | | | `-DeclRefExpr 0x55a9b9ab0b48 <col:13> 'uint32_t':'unsigned int' lvalue Var 0x55a9b9ab00a8 'global_counter' 'uint32_t':'unsigned int'
|       | | | `-IntegerLiteral 0x55a9b9ab0b60 <col:28> 'int' 1000
|       | | `-ImplicitCastExpr 0x55a9b9ab0bc0 <col:33> 'uint32_t':'unsigned int' <IntegralCast>
|       | |   `-IntegerLiteral 0x55a9b9ab0bb0 <col:33> 'int' 0
|       | `-CompoundStmt 0x55a9b9ab0c18 <line:23:38, line:25:9>
|       |   `-CallExpr 0x55a9b9ab0c00 <line:24:13, col:38> 'void'
|       |     `-ImplicitCastExpr 0x55a9b9ab0bf0 <col:13> 'void (*)()' <FunctionToPointerDecay>
|       |       `-DeclRefExpr 0x55a9b9ab0bb8 <col:13> 'void ()' Function 0x55a9b9ab0220 'update_hardware_watchdog' 'void ()'
|       `-IfStmt 0x55a9b9ab0ea0 <line:27:9, line:31:9>
`-FunctionDecl 0x55a9b9ab0f60 <line:35:1, line:38:1> line:35:5 main 'int ()'
"""
    with open('dumps/ast_dump.log', 'w') as f:
        f.write(ast_content)

    # 3. 构造生成的汇编代码 asm/output.s (关键点：删除了 update_hardware_watchdog)
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
        # 随机十六进制
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
