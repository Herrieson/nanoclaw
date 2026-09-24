import os
import math
import random
import uuid

os.makedirs('sim_data/logs', exist_ok=True)
os.makedirs('job_configs', exist_ok=True)
os.makedirs('result', exist_ok=True)

# Generate configs for target and decoy jobs
with open('job_configs/job_8811_env.ini', 'w') as f:
    f.write("[TOLERANCE]\nENERGY_TOL=0.010\nFORCE_TOL=0.020\nNOTES=Decoy job parameters\n")

with open('job_configs/job_9942_env.ini', 'w') as f:
    f.write("; Cluster Job Config dumped by SLURM\n")
    f.write("[TOLERANCE]\n")
    f.write("ENERGY_TOL=0.042\n")
    f.write("FORCE_TOL=0.055\n")
    f.write("MAX_STEPS=500\n")

def generate_chunk(job_id, steps, filename, is_decoy=False):
    filepath = os.path.join('sim_data/logs', filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        # Noise headers
        f.write(f"--- LOG CHUNK START | JOB {job_id} | NODE {random.randint(10, 99)} ---\n")
        f.write(f"TIMESTAMP: 2023-10-24T{random.randint(10, 23)}:{random.randint(10, 59)}:{random.randint(10, 59)}Z\n")
        
        if random.random() < 0.3:
            f.write("slurmstepd: warning: memory usage near limit!\n")
            f.write("0x7f8a9b2c 0x00000001 0x00000000 0x00000000\n")

        for step in steps:
            f.write(f"\n       Iteration    {step}(   1)\n")
            
            # SCF noise
            for scf in range(1, random.randint(5, 12)):
                ediff = random.uniform(-0.01, 0.01)
                f.write(f"       DAV:  {scf:2d}     -0.120E+04    {ediff:.2E}   -0.1E-03  {random.randint(100,500)}   0.1E-02\n")

            # Determine physics values
            if is_decoy:
                energy = -1000.0 - step * 0.5
                max_f = 2.0 * math.exp(-step/20)
            else:
                e_base = -1152.0
                if step <= 130:
                    energy = e_base + 100 * math.exp(-step / 30.0)
                    force_base = 0.1 + math.exp(-step / 30.0)
                else:
                    energy = e_base + math.sin(step) * 0.01
                    force_base = 0.02 + abs(math.cos(step)) * 0.01
                    
                # Trap conditions injections
                if step == 145:
                    force_base = 0.065 # > 0.055 (F_TOL)
                if step == 162:
                    force_base = 0.080 # secondary trap just in case
                max_f = force_base

            f.write("\n FREE ENERGIE OF THE ION-ELECTRON SYSTEM (eV)\n")
            f.write("  ---------------------------------------------------\n")
            f.write(f"  free  energy   TOTEN  =      {energy:.6f} eV\n\n")

            f.write(" POSITION                                       TOTAL-FORCE (eV/Angst)\n")
            f.write(" -----------------------------------------------------------------------------------\n")
            
            # Generate exactly one atom with the max_f component
            target_atom = random.randint(0, 7)
            target_axis = random.randint(0, 2)
            
            for atom in range(8):
                forces = [
                    random.uniform(-max_f * 0.4, max_f * 0.4),
                    random.uniform(-max_f * 0.4, max_f * 0.4),
                    random.uniform(-max_f * 0.4, max_f * 0.4)
                ]
                
                if atom == target_atom:
                    forces[target_axis] = max_f if random.choice([True, False]) else -max_f
                    
                x, y, z = random.uniform(0, 15), random.uniform(0, 15), random.uniform(0, 15)
                f.write(f"      {x:8.5f}      {y:8.5f}      {z:8.5f}         {forces[0]:10.6f}      {forces[1]:10.6f}      {forces[2]:10.6f}\n")
                
            f.write(" -----------------------------------------------------------------------------------\n")
            f.write(f" timing for ionic step {step} : CPU   {random.uniform(25, 45):.2f} s\n")

        f.write("--- LOG CHUNK END ---\n")

# Generate fragments for Decoy Job 8811
decoy_steps = list(range(1, 45))
random.shuffle(decoy_steps)
for i in range(0, len(decoy_steps), 3):
    chunk_steps = decoy_steps[i:i+3]
    generate_chunk(8811, chunk_steps, f"fragment_{uuid.uuid4().hex[:8]}.log", is_decoy=True)

# Generate fragments for Target Job 9942
target_steps = list(range(1, 181))
random.shuffle(target_steps)
for i in range(0, len(target_steps), random.randint(2, 5)):
    chunk_steps = target_steps[i:i+5]
    generate_chunk(9942, chunk_steps, f"chunk_{uuid.uuid4().hex[:12]}.txt", is_decoy=False)
