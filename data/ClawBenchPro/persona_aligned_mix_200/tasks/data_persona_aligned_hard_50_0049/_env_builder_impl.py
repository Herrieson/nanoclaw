import os
import random
import string

def generate_random_hash():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))

def build_env():
    # Directories setup
    dirs = ['dumps', 'bug_report', 'traces']
    for i in range(10):
        dirs.append(f"asm/zone_{i}")
        dirs.append(f"traces/run_group_{i}")
    
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # Decide the target (the culprit)
    target_module_id = random.randint(10, 89)
    target_hash = generate_random_hash()
    culprit_symbol = f"mod_{target_module_id:03d}_hw_watchdog_ping_{target_hash}"
    
    # 1. Build Traces (Noise + 1 Real Clue)
    for group in range(10):
        for run in range(20):
            trace_path = f"traces/run_group_{group}/sys_trace_{group}_{run}.log"
            module_id = group * 10 + (run % 10)
            
            with open(trace_path, 'w') as f:
                if module_id == target_module_id and group == (target_module_id // 10) and run == 13: # The single matching trace
                    f.write(f"SYS_BOOT: OK\nBOARD_REV: Rev-X9\n")
                    f.write(f"LOAD_MODULE: mod_{module_id:03d}\n")
                    f.write("EXEC_STATE: RUNNING\n")
                    f.write("... [HEX DUMP OMITTED] ...\n")
                    f.write(f"FATAL_ERR: WATCHDOG_TIMEOUT in module mod_{module_id:03d}\n")
                    f.write("SYSTEM_HALT\n")
                else:
                    # Fake traces
                    revs = ["Rev-A1", "Rev-B2", "Rev-C3", "Rev-X8"]
                    f.write(f"SYS_BOOT: OK\nBOARD_REV: {random.choice(revs)}\n")
                    f.write(f"LOAD_MODULE: mod_{module_id:03d}\n")
                    if random.random() > 0.8:
                        f.write("ERR: SEGFAULT (IGNORED)\n")
                    else:
                        f.write("SYS_EXIT: NORMAL\n")

    # 2. Build AST Dumps & Assembly
    # We have 100 modules (000 to 099)
    for chunk in range(10):
        ast_lines = []
        ast_lines.append(f"TranslationUnitDecl 0x{random.randint(0x1000,0x9000):04X} <<invalid sloc>> <invalid sloc>")
        
        for m in range(chunk * 10, chunk * 10 + 10):
            mod_name = f"mod_{m:03d}"
            
            # Module Entry Function
            ast_lines.append(f"|-FunctionDecl 0x{m}A000 <line:10> used {mod_name}_entry 'void ()'")
            ast_lines.append(f"| `-CompoundStmt 0x{m}A001")
            
            used_funcs = []
            dead_funcs = []
            
            # Generate 3-5 used normal functions
            for f_idx in range(random.randint(3, 5)):
                func_name = f"{mod_name}_worker_{f_idx}"
                used_funcs.append(func_name)
                ast_lines.append(f"|   |-CallExpr 0x{m}A10{f_idx}")
                ast_lines.append(f"|   | `-DeclRefExpr 0x{m}A20{f_idx} 'void ()' Function 0x{m}B00{f_idx} '{func_name}' 'void ()'")
            
            # If target module, inject the culprit into the AST calls
            if m == target_module_id:
                used_funcs.append(culprit_symbol) # It IS called
                ast_lines.append(f"|   |-CallExpr 0x{m}A109")
                ast_lines.append(f"|   | `-DeclRefExpr 0x{m}A209 'void ()' Function 0x{m}B009 '{culprit_symbol}' 'void ()'")
            
            # Generate 2-4 dead functions (NOT called in entry)
            for d_idx in range(random.randint(2, 4)):
                dead_name = f"{mod_name}_legacy_deadcode_{d_idx}"
                dead_funcs.append(dead_name)
                
            # Now append the FunctionDecls for all these functions
            for f_name in used_funcs:
                ast_lines.append(f"|-FunctionDecl 0x{random.randint(0x1000, 0xFFFF):X} <line:{random.randint(20,100)}> used {f_name} 'void ()'")
                ast_lines.append(f"| `-CompoundStmt 0x{random.randint(0x1000, 0xFFFF):X}")
            
            for d_name in dead_funcs:
                ast_lines.append(f"|-FunctionDecl 0x{random.randint(0x1000, 0xFFFF):X} <line:{random.randint(100,200)}> {d_name} 'void ()'")
                ast_lines.append(f"| `-CompoundStmt 0x{random.randint(0x1000, 0xFFFF):X}")

            # --- GENERATE ASSEMBLY FOR THIS MODULE ---
            asm_path = f"asm/zone_{chunk}/{mod_name}.s"
            asm_content = []
            asm_content.append(f"    .file	\"{mod_name}.c\"")
            asm_content.append(f"    .text")
            
            # Emitting assembly for entry
            asm_content.append(f"    .globl	{mod_name}_entry")
            asm_content.append(f"    .type	{mod_name}_entry, @function")
            asm_content.append(f"{mod_name}_entry:")
            asm_content.append(f"    ret")
            
            # Emitting assembly for used functions (BUT NOT THE CULPRIT)
            for f_name in used_funcs:
                if f_name == culprit_symbol:
                    # AGGRESSIVE DCE BUG SIMULATION: Skip emitting this symbol entirely!
                    continue
                asm_content.append(f"    .globl	{f_name}")
                asm_content.append(f"    .type	{f_name}, @function")
                asm_content.append(f"{f_name}:")
                asm_content.append(f"    nop")
                asm_content.append(f"    ret")
            
            # Note: Dead functions are correctly NOT emitted in assembly.
            
            with open(asm_path, 'w') as f:
                f.write("\n".join(asm_content) + "\n")
                
        # Write AST chunk
        with open(f"dumps/ast_shard_{chunk}.log", 'w') as f:
            f.write("\n".join(ast_lines) + "\n")

if __name__ == '__main__':
    build_env()
