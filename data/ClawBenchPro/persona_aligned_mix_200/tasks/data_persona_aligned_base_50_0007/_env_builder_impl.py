import os
import random
import math

def build_env():
    # Create required directories relative to the current working directory
    os.makedirs("simulation", exist_ok=True)
    os.makedirs("cluster_logs", exist_ok=True)
    os.makedirs("report", exist_ok=True)
    
    num_atoms = 64
    fatal_step = 14
    culprit_atom_idx = 42
    
    # Generate mock OSZICAR (Summary of SCF and Ionic steps)
    with open("simulation/OSZICAR", "w") as f_osz:
        f_osz.write(" vasp.6.3.0 20Jan22 (build Jan 24 2022 15:30:00) complex\n\n")
        
        for step in range(1, fatal_step + 1):
            if step < fatal_step:
                # Normal SCF convergence
                for scf in range(1, 16):
                    dE = -0.01 / scf if scf > 1 else -1.5
                    f_osz.write(f"       DAV:  {scf:2d}    -0.{5234 + step*10}E+03    {dE:9.3E}   -0.100E-02 \n")
                f_osz.write(f"{step} F= -.5234E+03 E0= -.5234E+03  d E = -0.00123\n\n")
            else:
                # Fatal step: SCF divergence
                f_osz.write(f"       DAV:   1    -0.5234E+03    0.000E+00 \n")
                f_osz.write(f"       DAV:   2     0.1023E+04    0.154E+04 \n")
                f_osz.write(f"       DAV:   3     0.8441E+04    0.741E+04 \n")
                f_osz.write(f"       DAV:   4     0.3129E+05    0.228E+05 \n")
                # Stops abruptly
    
    # Generate mock OUTCAR (Detailed verbose output, containing positions and forces)
    with open("simulation/OUTCAR", "w") as f_out:
        f_out.write(" vasp.6.3.0 20Jan22 (build Jan 24 2022 15:30:00) complex\n")
        f_out.write(" INCAR: \n")
        f_out.write("   PREC   = Accurate\n")
        f_out.write("   IBRION = 2\n")
        f_out.write("   NSW    = 100\n\n")
        
        # Add some garbage text to increase parsing difficulty
        for _ in range(500):
            f_out.write(f" k-point  {random.randint(1, 20)} :       {random.random():.4f}    {random.random():.4f}    {random.random():.4f}\n")
        
        for step in range(1, fatal_step + 1):
            f_out.write(f"\n-----------------------------------------\n")
            f_out.write(f" IONIC STEP {step:4d}\n")
            f_out.write(f"-----------------------------------------\n\n")
            
            # Write a lot of SCF energies
            scf_count = 15 if step < fatal_step else 4
            for scf in range(1, scf_count + 1):
                energy = -500.0 - step*1.5 + scf*0.1 if step < fatal_step else 500.0 * (10**scf)
                f_out.write(f"       Free energy of the ion-electron system (eV)\n")
                f_out.write(f"       alpha Z        PSCENC =         0.00000000\n")
                f_out.write(f"       E=  {energy:15.6f} \n\n")
            
            f_out.write(" POSITION                                       TOTAL-FORCE (eV/Angst)\n")
            f_out.write(" -----------------------------------------------------------------------------------\n")
            
            random.seed(42 + step) # Deterministic randomness for normal forces
            
            for atom_idx in range(1, num_atoms + 1):
                pos_x, pos_y, pos_z = random.uniform(0, 15), random.uniform(0, 15), random.uniform(0, 15)
                
                if step == fatal_step and atom_idx == culprit_atom_idx:
                    # Inject the catastrophic force
                    fx, fy, fz = 845.210, -991.330, 1502.440
                else:
                    # Normal small forces
                    fx, fy, fz = random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1)
                
                f_out.write(f" {pos_x:10.5f} {pos_y:10.5f} {pos_z:10.5f}    {fx:10.3f} {fy:10.3f} {fz:10.3f}\n")
                
            f_out.write(" -----------------------------------------------------------------------------------\n")
            
            if step < fatal_step:
                f_out.write(f" total drift:                                   {random.uniform(-0.01, 0.01):10.5f}  {random.uniform(-0.01, 0.01):10.5f}  {random.uniform(-0.01, 0.01):10.5f}\n")
            else:
                f_out.write(f" total drift:                                   {845.210/num_atoms:10.5f}  {-991.330/num_atoms:10.5f}  {1502.440/num_atoms:10.5f}\n")
                # Crash log representation in OUTCAR
                f_out.write("\n===================================================================================\n")
                f_out.write("=   BAD TERMINATION OF ONE OF YOUR APPLICATION PROCESSES\n")
                f_out.write("=   PID 998242 RUNNING AT node-104\n")
                f_out.write("=   EXIT CODE: 139\n")
                f_out.write("=   CLEANING UP REMAINING PROCESSES\n")
                f_out.write("===================================================================================\n")
    
    # Generate mock SLURM log
    with open("cluster_logs/slurm-998242.out", "w") as f_slurm:
        f_slurm.write("Loading intel/2021.4.0\n")
        f_slurm.write("Loading openmpi/4.1.2\n")
        f_slurm.write("Starting VASP simulation...\n")
        f_slurm.write("Warning: IBRION=2 with large step size might be unstable.\n")
        for _ in range(50):
            f_slurm.write("LDIAG:  routine ZHEEV returns INFO = 0\n")
        f_slurm.write("===================================================================================\n")
        f_slurm.write("forrtl: severe (174): SIGSEGV, segmentation fault occurred\n")
        f_slurm.write("Image              PC                Routine            Line        Source\n")
        f_slurm.write("vasp_std           0000000000A1B2C3  Unknown               Unknown  Unknown\n")
        f_slurm.write("vasp_std           0000000000B2C3D4  Unknown               Unknown  Unknown\n")
        f_slurm.write("libc.so.6          00007F8A9B8C7D8E  Unknown               Unknown  Unknown\n")
        f_slurm.write("srun: error: node-104: task 0: Segmentation fault (core dumped)\n")

if __name__ == '__main__':
    build_env()
