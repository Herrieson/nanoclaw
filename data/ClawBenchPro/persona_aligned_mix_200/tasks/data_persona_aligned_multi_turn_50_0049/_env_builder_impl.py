import os
import argparse

def build_turn_1():
    os.makedirs("src", exist_ok=True)
    os.makedirs("ast", exist_ok=True)
    os.makedirs("asm_O0", exist_ok=True)
    os.makedirs("asm_O3", exist_ok=True)

    # --- src files ---
    with open("src/crypto.c", "w") as f:
        f.write("void secure_wipe(int *addr, int len) {\n  for (int i=0; i<len; i++) {\n    *(volatile int*)(addr + i) = 0;\n  }\n}\nvoid encrypt_block(int *data) {\n  data[0] ^= 0x55;\n}\n")
    with open("src/state.c", "w") as f:
        f.write("void dispatch_event(int event_id) {\n  hardware_trigger(event_id);\n}\nvoid update_counter() {\n  counter++;\n}\n")
    with open("src/math_ops.c", "w") as f:
        f.write("int matrix_det(int *mat) {\n  return mat[0]*mat[3] - mat[1]*mat[2];\n}\n")
    with open("src/network.c", "w") as f:
        f.write("void process_packet(int *pkt) {\n  int header = pkt[0];\n  int payload_len = pkt[1];\n  // process\n}\n")

    # --- AST files ---
    with open("ast/crypto.ast", "w") as f:
        f.write("FunctionDecl: secure_wipe\n  CompoundStmt\n    ForStmt\n      BinaryOperator: = (Volatile: True)\n        DeclRefExpr: addr\n        IntegerLiteral: 0\nFunctionDecl: encrypt_block\n  CompoundStmt\n    CompoundAssignOperator: ^=\n      ArraySubscriptExpr\n        DeclRefExpr: data\n")
    with open("ast/state.ast", "w") as f:
        f.write("FunctionDecl: dispatch_event\n  CompoundStmt\n    CallExpr: hardware_trigger (SideEffect: True)\n      DeclRefExpr: event_id\nFunctionDecl: update_counter\n  CompoundStmt\n    UnaryOperator: ++\n      DeclRefExpr: counter\n")
    with open("ast/math_ops.ast", "w") as f:
        f.write("FunctionDecl: matrix_det\n  CompoundStmt\n    ReturnStmt\n      BinaryOperator: -\n        BinaryOperator: *\n")
    with open("ast/network.ast", "w") as f:
        f.write("FunctionDecl: process_packet\n  CompoundStmt\n    DeclStmt\n      VarDecl: header\n")

    # --- asm_O0 ---
    with open("asm_O0/crypto.s", "w") as f:
        f.write("secure_wipe:\n.L1:\n  li r3, 0\n  st.v r3, [r1]\n  add r1, r1, 4\n  sub r2, r2, 1\n  bnez r2, .L1\n  ret\n\nencrypt_block:\n  ld r4, [r1]\n  xor r4, r4, 0x55\n  st r4, [r1]\n  ret\n")
    with open("asm_O0/state.s", "w") as f:
        f.write("dispatch_event:\n  call hardware_trigger\n  ret\n\nupdate_counter:\n  la r1, counter\n  ld r2, [r1]\n  add r2, r2, 1\n  st r2, [r1]\n  ret\n")
    with open("asm_O0/math_ops.s", "w") as f:
        f.write("matrix_det:\n  ld r2, [r1]\n  ld r3, [r1, 12]\n  mul r4, r2, r3\n  ret\n")
    with open("asm_O0/network.s", "w") as f:
        f.write("process_packet:\n  sub sp, sp, 16\n  st r1, [sp, 0]\n  ld r2, [r1]\n  ld r3, [r1, 4]\n  add sp, sp, 16\n  ret\n")

    # --- asm_O3 (Buggy DCE logic) ---
    with open("asm_O3/crypto.s", "w") as f:
        f.write("secure_wipe:\n  ret\n\nencrypt_block:\n  ld r4, [r1]\n  xor r4, r4, 0x55\n  st r4, [r1]\n  ret\n")
    with open("asm_O3/state.s", "w") as f:
        f.write("dispatch_event:\n  ret\n\nupdate_counter:\n  la r1, counter\n  ld r2, [r1]\n  add r2, r2, 1\n  st r2, [r1]\n  ret\n")
    with open("asm_O3/math_ops.s", "w") as f:
        f.write("matrix_det:\n  ld r2, [r1]\n  ld r3, [r1, 12]\n  mul r4, r2, r3\n  ret\n")
    with open("asm_O3/network.s", "w") as f:
        f.write("process_packet:\n  sub sp, sp, 16\n  st r1, [sp, 0]\n  ld r2, [r1]\n  ld r3, [r1, 4]\n  add sp, sp, 16\n  ret\n")

def build_turn_2():
    os.makedirs("new_asm_O3", exist_ok=True)
    with open("patch_notes.md", "w") as f:
        f.write("# Zephyr-v2 Hardware Errata\n\n**CRITICAL PIPELINE HAZARD**: Load-Use Stall.\nIf any register is used as the destination of a `ld` (load) instruction, it CANNOT be used as a source operand in the IMMEDIATELY following instruction. Doing so will cause an unrecoverable pipeline stall.\n\nExample of BUGGY code:\nld r7, [r1]\nadd r2, r7, r3  # Hazard: r7 is used immediately!\n\nExample of SAFE code:\nld r7, [r1]\nnop             # padding instruction breaks the hazard\nadd r2, r7, r3\n")

    # Fixed DCE, but introduced load-use hazards in other functions
    with open("new_asm_O3/crypto.s", "w") as f:
        f.write("secure_wipe:\n.L1:\n  li r3, 0\n  st.v r3, [r1]\n  add r1, r1, 4\n  sub r2, r2, 1\n  bnez r2, .L1\n  ret\n\nencrypt_block:\n  ld r4, [r1]\n  xor r4, r4, 0x55\n  st r4, [r1]\n  ret\n")
        # encrypt_block has load-use hazard on r4

    with open("new_asm_O3/state.s", "w") as f:
        f.write("dispatch_event:\n  call hardware_trigger\n  ret\n\nupdate_counter:\n  la r1, counter\n  ld r2, [r1]\n  add r2, r2, 1\n  st r2, [r1]\n  ret\n")
        # update_counter has load-use hazard on r2

    with open("new_asm_O3/math_ops.s", "w") as f:
        f.write("matrix_det:\n  ld r2, [r1]\n  nop\n  ld r3, [r1, 12]\n  nop\n  mul r4, r2, r3\n  ret\n")

    with open("new_asm_O3/network.s", "w") as f:
        f.write("process_packet:\n  sub sp, sp, 16\n  st r1, [sp, 0]\n  ld r2, [r1]\n  nop\n  ld r3, [r1, 4]\n  ld r4, [sp, 24]\n  add sp, sp, 16\n  ret\n")
        # Safe from load-use hazard, but contains a silent stack bounds bug for turn 3

def build_turn_3():
    os.makedirs("traces", exist_ok=True)
    with open("linker_map.txt", "w") as f:
        f.write("=== System Memory Map ===\n0x10000 - secure_wipe\n0x10040 - encrypt_block\n0x10080 - dispatch_event\n0x100A0 - update_counter\n0x10100 - matrix_det\n0x10200 - process_packet\n")
    
    with open("traces/crash.log", "w") as f:
        f.write("FATAL HARDWARE EXCEPTION: Memory Access Violation (Out of Bounds)\nRegister Dump:\nr1: 0x20004000\nr2: 0x00000014\nr3: 0x00000080\nr4: 0x00000000\nsp: 0x20008F00\npc: 0x10214\n")
        # PC: 0x10214 maps to process_packet (0x10200 + 0x14).
        # Offset 0x14 = 20 bytes = instruction at index 5.
        # 0x00: sub sp, sp, 16
        # 0x04: st r1, [sp, 0]
        # 0x08: ld r2, [r1]
        # 0x0C: nop
        # 0x10: ld r3, [r1, 4]
        # 0x14: ld r4, [sp, 24]  <- 越界访问出崩溃点

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
