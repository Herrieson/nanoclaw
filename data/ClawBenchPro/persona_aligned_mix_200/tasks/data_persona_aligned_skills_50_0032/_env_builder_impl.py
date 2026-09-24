import os
import math
import random
import json
import base64

def build_env():
    os.makedirs('sim_data', exist_ok=True)
    os.makedirs('result', exist_ok=True)

    outcar_path = 'sim_data/OUTCAR_fragment.log'
    slurm_path = 'sim_data/slurm-89912.out'
    traj_path = 'sim_data/MD_traj.xdat'

    # 生成损坏的 OUTCAR，不包含任何有效的 TOTEN 和 力数据
    with open(outcar_path, 'w', encoding='utf-8') as f:
        f.write(" vasp.6.3.0 20Jan22 (build Jan 24 2022 15:30:00) complex\n")
        f.write(" POSCAR, INCAR and KPOINTS ok, starting setup\n")
        f.write(" WARNING: grid for exact exchange is too sparse\n\n")
        f.write(" IO_ERROR: FORCE DATA AND ENERGY DATA CORRUPTED DURING DISK SYNC.\n")
        
        for step in range(1, 46):
            f.write(f"\n       Iteration    {step}(   1)\n")
            for scf in range(1, random.randint(3, 8)):
                ediff = random.uniform(-0.01, 0.01)
                f.write(f"       DAV:  {scf:2d}     NaN    {ediff:.2E}   NaN  {random.randint(100,500)}   NaN\n")
            f.write("\n FREE ENERGIE OF THE ION-ELECTRON SYSTEM (eV)\n")
            f.write("  ---------------------------------------------------\n")
            f.write(f"  free  energy   TOTEN  =      *** NaN *** eV\n\n")

    # 生成包含真实能量和最大受力的轨迹数据，将其伪装成定制的二进制文件
    traj_data = []
    energy_base = -1200.0
    
    for step in range(1, 46):
        if step <= 20:
            energy = energy_base - (20 - (20 - step)**1.3)
            max_f = 0.8 - 0.035 * step
        else:
            energy = energy_base - 20.0 + math.sin(step * 1.5) * 0.01
            max_f = 0.09 + math.cos(step * 2.1) * 0.02

        traj_data.append({
            "step": step,
            "TOTEN": round(energy, 6),
            "max_force": round(max_f, 6)
        })
        
    # 用 base64 编码假装是自定义扩展格式，强迫 Agent 调用 parser
    json_bytes = json.dumps(traj_data).encode('utf-8')
    encoded_traj = base64.b64encode(json_bytes).decode('utf-8')
    
    with open(traj_path, 'w', encoding='utf-8') as f:
        f.write("XDAT_TRAJ_V1.0\n")
        f.write(encoded_traj)

    # 报错日志
    with open(slurm_path, 'w', encoding='utf-8') as f:
        f.write("slurmstepd: error: *** JOB 89912 ON node042 CANCELLED AT 2023-10-24T03:15:00 DUE TO TIME LIMIT ***\n")
        f.write("Memory dump at crash:\n")
        f.write("0x7f8a9b2c 0x00000001 0x00000000 0x00000000\n")
        f.write("0x7f8a9b3c 0xDEADBEEF 0xBAADF00D 0x00000000\n")
        f.write("mpirun noticed that process rank 3 with PID 10243 on node node042 exited on signal 9 (Killed).\n")

if __name__ == "__main__":
    build_env()
