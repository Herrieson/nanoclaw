import os
import argparse
import math

def write_poscar(filepath, elements, counts):
    content = f"Material Structure\n1.0\n"
    content += "  5.0 0.0 0.0\n  0.0 5.0 0.0\n  0.0 0.0 5.0\n"
    content += " ".join(elements) + "\n"
    content += " ".join(map(str, counts)) + "\n"
    content += "Cartesian\n"
    total = sum(counts)
    for i in range(total):
        content += f"  {i*0.1:.5f}  {i*0.1:.5f}  {i*0.1:.5f}\n"
    with open(filepath, 'w') as f:
        f.write(content)

def write_oszicar(filepath, steps, dE_values):
    with open(filepath, 'w') as f:
        for i in range(steps):
            f.write(f"       {i+1} F= -.1000E+03 E0= -.1000E+03  d E =  {dE_values[i]:.5f}\n")

def write_outcar_forces(filepath, steps, atoms_count, target_step=None, target_atom=None, target_force=None, default_force=0.5):
    with open(filepath, 'w') as f:
        for s in range(steps):
            f.write(f"--- Ion Step {s+1} ---\n")
            f.write("Position                       Force (eV/Angst)\n")
            for a in range(atoms_count):
                if s + 1 == target_step and a == target_atom:
                    f_val = target_force / math.sqrt(3)
                    f.write(f"  0.0  0.0  0.0       {f_val:.5f}  {f_val:.5f}  {f_val:.5f}\n")
                else:
                    df = default_force / math.sqrt(3)
                    f.write(f"  0.0  0.0  0.0       {df:.5f}  {df:.5f}  {df:.5f}\n")

def write_magnetization(filepath, steps, mag_values):
    with open(filepath, 'w') as f:
        f.write("Ion_Step  Total_Magnetization\n")
        for i in range(steps):
             f.write(f"  {i+1}        {mag_values[i]:.5f}\n")

def build_turn_1():
    os.makedirs("input_structures", exist_ok=True)
    os.makedirs("vasp_logs/A01", exist_ok=True)
    os.makedirs("vasp_logs/A02", exist_ok=True)
    os.makedirs("vasp_logs/A03", exist_ok=True)

    # A01: Normal
    write_poscar("input_structures/POSCAR_A01", ["Li", "Mn", "O"], [4, 4, 8])
    write_oszicar("vasp_logs/A01/OSZICAR", 20, [0.1]*20)
    write_outcar_forces("vasp_logs/A01/OUTCAR_forces.log", 20, 16)

    # A02: Crashes at step 15. Force exceeds 2.0 (target: Co atom, which is atom index 8)
    write_poscar("input_structures/POSCAR_A02", ["Li", "Mn", "Co", "O"], [4, 3, 1, 8])
    dE_A02 = [0.1]*14 + [5.8] + [0.1]*5
    write_oszicar("vasp_logs/A02/OSZICAR", 20, dE_A02)
    # atom index 8 is Co (0-3 Li, 4-6 Mn, 7 Co). Wait, indices are 0-based. So 7 is Co.
    write_outcar_forces("vasp_logs/A02/OUTCAR_forces.log", 20, 16, target_step=15, target_atom=7, target_force=3.2)

    # A03: Initial relaxation jump (Step 2), which is normal, but then fine. 
    # Wait, prompt says: "前3个离子步震荡正常, 别当崩溃". 
    # Let's make step 2 jump big, but step 12 actually crashes.
    write_poscar("input_structures/POSCAR_A03", ["Li", "Mn", "Ni", "O"], [4, 3, 1, 8])
    dE_A03 = [0.1, 8.5, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 6.2, 0.1, 0.1, 0.1]
    write_oszicar("vasp_logs/A03/OSZICAR", 15, dE_A03)
    write_outcar_forces("vasp_logs/A03/OUTCAR_forces.log", 15, 16)

def build_turn_2():
    # Keep turn 1 structures, add B batch
    os.makedirs("input_structures", exist_ok=True)
    os.makedirs("vasp_logs/B01", exist_ok=True)
    os.makedirs("vasp_logs/B02", exist_ok=True)
    os.makedirs("vasp_logs/B03", exist_ok=True)

    # B01: The ultimate survivor. Good forces, good mag.
    write_poscar("input_structures/POSCAR_B01", ["Li", "Mn", "Fe", "O"], [5, 2, 1, 8])
    write_oszicar("vasp_logs/B01/OSZICAR", 25, [0.05]*25)
    write_outcar_forces("vasp_logs/B01/OUTCAR_forces.log", 25, 16, default_force=0.3)
    write_magnetization("vasp_logs/B01/magnetization.dat", 25, [3.0]*25)

    # B02: The TRAP! Force at step 18 is 1.95 (close to 2.0 but not crossing). 
    # Mag drops from 2.5 to -1.2 (reversal).
    write_poscar("input_structures/POSCAR_B02", ["Li", "Mn", "Ru", "O"], [4, 3, 1, 8])
    write_oszicar("vasp_logs/B02/OSZICAR", 25, [0.2]*25)
    write_outcar_forces("vasp_logs/B02/OUTCAR_forces.log", 25, 16, target_step=18, target_atom=5, target_force=1.95)
    mag_B02 = [2.5]*17 + [-1.2]*8
    write_magnetization("vasp_logs/B02/magnetization.dat", 25, mag_B02)

    # B03: Crosses the force dead-line. Force = 4.5. Mag is stable.
    write_poscar("input_structures/POSCAR_B03", ["Li", "Mn", "Ti", "O"], [4, 3, 1, 8])
    write_oszicar("vasp_logs/B03/OSZICAR", 20, [0.3]*20)
    write_outcar_forces("vasp_logs/B03/OUTCAR_forces.log", 20, 16, target_step=10, target_atom=2, target_force=4.5)
    write_magnetization("vasp_logs/B03/magnetization.dat", 20, [1.5]*20)

def build_turn_3():
    # Turn 3 does not necessarily need new files to be generated, 
    # it relies on the complex logic of resolving multi-turn memories.
    # We create a placeholder file just to simulate some environment shift, 
    # without destroying any existing data.
    with open("hpc_quota_warning.txt", "w") as f:
         f.write("WARNING: Compute limits exceeded. Terminating unpromising jobs is highly recommended.\n")

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
