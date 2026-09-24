import os
import math
import random

os.makedirs('sim_data', exist_ok=True)
os.makedirs('result', exist_ok=True)

outcar_path = 'sim_data/OUTCAR_fragment.log'
slurm_path = 'sim_data/slurm-89912.out'

with open(outcar_path, 'w', encoding='utf-8') as f:
    f.write(" vasp.6.3.0 20Jan22 (build Jan 24 2022 15:30:00) complex\n")
    f.write(" POSCAR, INCAR and KPOINTS ok, starting setup\n")
    f.write(" WARNING: grid for exact exchange is too sparse\n\n")

    energy_base = -1200.0
    
    for step in range(1, 45):
        f.write(f"\n       Iteration    {step}(   1)\n")
        
        for scf in range(1, random.randint(15, 30)):
            ediff = random.uniform(-0.01, 0.01)
            f.write(f"       DAV:  {scf:2d}     -0.120E+04    {ediff:.2E}   -0.1E-03  {random.randint(100,500)}   0.1E-02\n")

        if step <= 20:
            energy = energy_base - (20 - (20 - step)**1.3)
            max_f = 0.8 - 0.035 * step
        else:
            energy = energy_base - 20.0 + math.sin(step * 1.5) * 0.01
            max_f = 0.09 + math.cos(step * 2.1) * 0.02

        f.write("\n FREE ENERGIE OF THE ION-ELECTRON SYSTEM (eV)\n")
        f.write("  ---------------------------------------------------\n")
        f.write(f"  free  energy   TOTEN  =      {energy:.6f} eV\n\n")

        f.write(" POSITION                                       TOTAL-FORCE (eV/Angst)\n")
        f.write(" -----------------------------------------------------------------------------------\n")
        
        for atom in range(8):
            fx = random.uniform(-max_f * 0.5, max_f * 0.5)
            fy = random.uniform(-max_f * 0.5, max_f * 0.5)
            fz = random.uniform(-max_f * 0.5, max_f * 0.5)
            
            if atom == 3:
                fx = max_f if random.choice([True, False]) else -max_f
                
            x, y, z = random.uniform(0, 15), random.uniform(0, 15), random.uniform(0, 15)
            f.write(f"      {x:8.5f}      {y:8.5f}      {z:8.5f}         {fx:10.6f}      {fy:10.6f}      {fz:10.6f}\n")
            
        f.write(" -----------------------------------------------------------------------------------\n")
        f.write(f" timing for ionic step {step} : CPU   {random.uniform(25, 45):.2f} s\n")
        f.write(" BRION: g(F)=  0.421E-01 g(S)=  0.000E+00\n")

with open(slurm_path, 'w', encoding='utf-8') as f:
    f.write("slurmstepd: error: *** JOB 89912 ON node042 CANCELLED AT 2023-10-24T03:15:00 DUE TO TIME LIMIT ***\n")
    f.write("Memory dump at crash:\n")
    f.write("0x7f8a9b2c 0x00000001 0x00000000 0x00000000\n")
    f.write("0x7f8a9b3c 0xDEADBEEF 0xBAADF00D 0x00000000\n")
    f.write("mpirun noticed that process rank 3 with PID 10243 on node node042 exited on signal 9 (Killed).\n")
