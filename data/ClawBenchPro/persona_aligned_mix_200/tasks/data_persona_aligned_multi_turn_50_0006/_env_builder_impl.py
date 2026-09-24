import os
import argparse
import random

def create_trial_log(filepath, channels, stimulus_idx, bad_spikes=None):
    with open(filepath, 'w') as f:
        f.write("=== BCI ACQUISITION SYSTEM DEBUG LOG ===\n")
        f.write(f"SYSTEM_INIT_OK: TRUE\n")
        f.write("COMMENCING DATA STREAM...\n")
        
        for i in range(20):
            if i == stimulus_idx:
                f.write(f"SYS_MSG [T={i}]: MARKER: STIMULUS_ON detected from trigger board.\n")
            
            f.write(f"DATA [T={i}]: ")
            ch_data = []
            for ch_name, base_val in channels.items():
                val = base_val + random.uniform(-5.0, 5.0)
                
                # Inject artificial spikes (artifacts)
                if bad_spikes and ch_name in bad_spikes and bad_spikes[ch_name]:
                    # Spike over 150uV
                    val = random.choice([160.5, -172.3, 201.0, -155.8])
                    bad_spikes[ch_name] = False # only spike once per trial for simplicity
                    
                ch_data.append(f"{ch_name}={val:.2f}")
                
            f.write(" | ".join(ch_data) + " // chk_sum_pass\n")
        f.write("=== STREAM END ===\n")

def build_turn_1():
    os.makedirs("session_A_data", exist_ok=True)
    
    # Base ERP responses (post-stimulus average boost)
    # C3 is highest, FP1 is second, O1 is low, Pz is mid, C4 is theoretically highest but will be ruined.
    channels_base = {"CH_FP1": 10.0, "CH_C3": 25.0, "CH_C4": 40.0, "CH_O1": 5.0, "CH_PZ": 15.0}
    
    # 5 trials for Session A
    # Rules: threshold is 150uV. >30% (i.e. >=2 out of 5 trials) makes it a BAD channel.
    # We will make CH_C4 a BAD channel in Session A (spikes in trial 1 and 3).
    for trial in range(1, 6):
        stim_idx = random.randint(2, 5)
        bad_spikes = {}
        if trial in [1, 3]:
            bad_spikes["CH_C4"] = True
            
        # modify base val for post stimulus simulation
        dynamic_channels = dict(channels_base)
        
        create_trial_log(f"session_A_data/trial_00{trial}.log", dynamic_channels, stim_idx, bad_spikes)

def build_turn_2():
    os.makedirs("session_B_data", exist_ok=True)
    
    # Same channels, 5 new trials.
    # Trap: CH_C4 might look good here, but it should be excluded based on Turn 1 memory!
    # In Session B, we will make CH_O1 a BAD channel (spikes in trial 2 and 5).
    # Remaining GOOD in BOTH: CH_FP1, CH_C3, CH_PZ.
    # Their ERP ranks: CH_C3 > CH_PZ > CH_FP1
    channels_base = {"CH_FP1": 12.0, "CH_C3": 28.0, "CH_C4": 45.0, "CH_O1": 4.0, "CH_PZ": 18.0}
    
    for trial in range(1, 6):
        stim_idx = random.randint(2, 5)
        bad_spikes = {}
        if trial in [2, 5]:
            bad_spikes["CH_O1"] = True
            
        dynamic_channels = dict(channels_base)
        create_trial_log(f"session_B_data/trial_00{trial}.log", dynamic_channels, stim_idx, bad_spikes)

def build_turn_3():
    os.makedirs("hardware_specs", exist_ok=True)
    with open("hardware_specs/crosstalk_matrix.txt", "w") as f:
        f.write("=== NEURO-AMP CROSSTALK WARNING ===\n")
        f.write("Do not route the following pairs simultaneously due to spatial aliasing:\n")
        f.write("- CH_FP1 <--> CH_C3 (CRITICAL RISK)\n")
        f.write("- CH_O1 <--> CH_C4 (MODERATE RISK)\n")
        f.write("- CH_PZ <--> CH_C4 (CRITICAL RISK)\n")
        f.write("\nFailure to comply will result in system thermal shutdown.\n")

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
