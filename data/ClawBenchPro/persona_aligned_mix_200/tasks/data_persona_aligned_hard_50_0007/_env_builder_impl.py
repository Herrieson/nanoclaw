import os
import random
import hashlib
import math
import json

def build_env():
    # Directories
    os.makedirs("cluster_logs", exist_ok=True)
    os.makedirs("simulation/scratch", exist_ok=True)
    os.makedirs("report", exist_ok=True)

    random.seed(42) # Ensuring reproducibility
    
    # 1. Generate 500 noise SLURM logs
    job_names_decoy = ["H2O_MD", "Graphene_dos", "MOF74_relax_test", "Cu_surface", "Perovskite_opt", "MOF74_FAILED_old"]
    
    target_job_id = 83921
    decoy_crash_job_ids = [10234, 45912, 77210] # Decoy jobs that also diverged

    for i in range(10000, 10500):
        job_id = target_job_id if i == 10250 else (decoy_crash_job_ids.pop() if decoy_crash_job_ids else i)
        
        with open(f"cluster_logs/slurm-{job_id}.out", "w") as f:
            f.write("Loading intel/2021.4.0\nLoading openmpi/4.1.2\n")
            if job_id == target_job_id:
                f.write("[WRAPPER] Job Name: MOF74_CRASH_TEST_FINAL_run\n")
            elif job_id in [10234, 45912, 77210]:
                f.write(f"[WRAPPER] Job Name: MOF74_FAILED_old_run_{job_id}\n")
            else:
                f.write(f"[WRAPPER] Job Name: {random.choice(job_names_decoy)}\n")
            
            f.write(f"[WRAPPER] Allocated Scratch: simulation/scratch/job_{job_id}\n")
            f.write("Starting VASP simulation...\n")
            
            if job_id == target_job_id:
                f.write("[WRAPPER] Recovering from checkpoint...\n")
                f.write("[WRAPPER] Writing to continuation chunk_04\n")
                f.write("forrtl: severe (174): SIGSEGV, segmentation fault occurred\n")
            elif job_id in [10234, 45912, 77210]:
                f.write("[WRAPPER] Writing to continuation chunk_02\n")
                f.write("forrtl: severe (174): SIGSEGV, segmentation fault occurred\n")
            else:
                f.write("[WRAPPER] Job finished successfully.\n")

    # 2. Build directories and data for the target job and decoys
    jobs_to_create = [target_job_id, 10234, 45912, 77210]
    
    for j_id in jobs_to_create:
        is_target = (j_id == target_job_id)
        chunk_dir = f"simulation/scratch/job_{j_id}/chunk_04" if is_target else f"simulation/scratch/job_{j_id}/chunk_02"
        os.makedirs(f"{chunk_dir}/forces_dump", exist_ok=True)
        
        num_atoms = 256
        fatal_step = 142 if is_target else random.randint(50, 90)
        culprit_atom_idx = 187 if is_target else random.randint(1, 100)
        
        # Write OSZICAR
        with open(f"{chunk_dir}/OSZICAR", "w") as f_osz:
            f_osz.write(" vasp.6.3.0 20Jan22 (build Jan 24 2022 15:30:00) complex\n\n")
            start_step = 120 if is_target else 1
            
            for step in range(start_step, fatal_step + 1):
                if step < fatal_step:
                    f_osz.write(f"{step} F= -.1245E+04 E0= -.1245E+04  d E = -0.00123\n\n")
                else:
                    # Divergence
                    f_osz.write(f"       DAV:   1    -0.1245E+04    0.000E+00 \n")
                    f_osz.write(f"       DAV:   2     0.2023E+04    0.154E+04 \n")
                    f_osz.write(f"{step} F= +.9821E+05 E0= +.9821E+05  d E = +.89412\n\n") # Exploded Energy

        # Write sync.log and shards
        with open(f"{chunk_dir}/sync.log", "w") as f_sync:
            for step in range(start_step, fatal_step + 1):
                shard_hash = hashlib.md5(f"{j_id}_{step}".encode()).hexdigest()[:12]
                f_sync.write(f"[INFO] Ionic step {step:03d} forces synced to forces_dump/shard_{shard_hash}.txt\n")
                
                # Write shard file
                with open(f"{chunk_dir}/forces_dump/shard_{shard_hash}.txt", "w") as f_shard:
                    f_shard.write(" POSITION                                       TOTAL-FORCE (eV/Angst)\n")
                    f_shard.write(" -----------------------------------------------------------------------------------\n")
                    
                    for atom_idx in range(1, num_atoms + 1):
                        px, py, pz = random.uniform(0, 20), random.uniform(0, 20), random.uniform(0, 20)
                        
                        if step == fatal_step and atom_idx == culprit_atom_idx:
                            if is_target:
                                fx, fy, fz = 1420.500, -2301.200, 3102.800
                            else:
                                fx, fy, fz = 999.000, 999.000, 999.000 # Decoy large force
                        else:
                            fx, fy, fz = random.uniform(-2.0, 2.0), random.uniform(-2.0, 2.0), random.uniform(-2.0, 2.0)
                        
                        f_shard.write(f" {px:10.5f} {py:10.5f} {pz:10.5f}    {fx:10.3f} {fy:10.3f} {fz:10.3f}\n")
                    f_shard.write(" -----------------------------------------------------------------------------------\n")

    # Add some random junk directories to simulation/scratch
    for i in range(20):
        junk_id = random.randint(20000, 90000)
        os.makedirs(f"simulation/scratch/job_{junk_id}/chunk_01/forces_dump", exist_ok=True)
        with open(f"simulation/scratch/job_{junk_id}/chunk_01/OSZICAR", "w") as f:
            f.write("Empty or corrupted file.\n")

if __name__ == '__main__':
    build_env()
