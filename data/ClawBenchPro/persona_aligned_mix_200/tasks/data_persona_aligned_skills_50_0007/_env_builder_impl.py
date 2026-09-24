import os
import random
import struct

def build_env():
    # Create required directories relative to the current working directory
    os.makedirs("simulation", exist_ok=True)
    os.makedirs("cluster_logs", exist_ok=True)
    os.makedirs("report", exist_ok=True)
    
    fatal_step = 14
    
    # 1. Generate mock OSZICAR (Summary of SCF and Ionic steps) - Plain text to find the fatal step
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
    
    # 2. Generate mock OUTCAR.dat - Encrypted/Corrupted binary file (replaces the original OUTCAR plaintext)
    # This forces the agent to use the specialized skills rather than reading it.
    with open("simulation/OUTCAR.dat", "wb") as f_out_bin:
        # Write some fake binary header
        f_out_bin.write(b"VASP_BIN_OUT_V6.3.0_DUMP\n")
        f_out_bin.write(b"\x00\x01\x02\x03\x04\x05\x06\x07")
        # Write 2MB of random garbage to simulate a corrupted binary memory dump
        for _ in range(2048):
            random_bytes = bytearray(random.getrandbits(8) for _ in range(1024))
            f_out_bin.write(random_bytes)
    
    # 3. Generate mock SLURM log
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
        f_slurm.write("FATAL: OUTCAR file descriptor closed unexpectedly. File corrupted.\n")

if __name__ == '__main__':
    build_env()
