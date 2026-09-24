import os
import argparse
import json
import csv

def build_turn_1():
    os.makedirs("vcd_logs", exist_ok=True)
    os.makedirs("doc", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    vcd_1_content = """$date today $end
$timescale 1ns $end
$scope module top $end
$var wire 1 ! clk $end
$var wire 1 " rstn $end
$var wire 8 # bus_data $end
$upscope $end
$enddefinitions $end
#0
0!
0"
b00000000 #
#5
1!
#10
0!
1"
b10101010 #
#15
1!
b10X01010 #
#20
0!
"""
    with open("vcd_logs/test_01.vcd", "w") as f:
        f.write(vcd_1_content)

    vcd_2_content = """$date today $end
$timescale 1ns $end
$scope module top $end
$var wire 1 ! clk $end
$var wire 1 " rstn $end
$var wire 8 # bus_data $end
$upscope $end
$enddefinitions $end
#0
0!
0"
bX1111111 #
#5
1!
#10
0!
1"
b01111111 #
#15
1!
#20
0!
b11111Z11 #
#25
1!
"""
    with open("vcd_logs/test_02.vcd", "w") as f:
        f.write(vcd_2_content)

    mapping = {
        "0": "SPI_CTRL",
        "1": "I2C_CTRL",
        "2": "DMA_ENGINE",
        "3": "UART_MAC",
        "4": "GPIO_TOP",
        "5": "L2_CACHE_CTRL",
        "6": "FPU_EX",
        "7": "MMU_CORE"
    }
    with open("doc/module_mapping.json", "w") as f:
        json.dump(mapping, f, indent=4)


def build_turn_2():
    os.makedirs("timing_reports", exist_ok=True)
    os.makedirs("rules", exist_ok=True)

    rules_content = """## Global Timing Rules for 7nm node

To calculate the Real Slack for any given path, you must apply the module-specific penalty to the reported slack from the timing report.

Formula:
Real_Slack = Reported_Slack - (Penalty * 0.01)

Redline Thresholds:
- Setup Real_Slack MUST be >= 0.05
- Hold Real_Slack MUST be >= 0.02

If a module's Real_Slack is below the threshold, it is considered a Timing Violation.
The Shortfall is calculated as: Threshold - Real_Slack.
"""
    with open("rules/lib_timing_rules.txt", "w") as f:
        f.write(rules_content)

    rep_l2 = """======================================
Timing Report: L2_CACHE_CTRL
======================================
Path Type: Max (Setup)
Reported Setup Slack: 0.08 ns
Module Deviation Penalty: 5

Conclusion: TBD
"""
    with open("timing_reports/L2_CACHE_CTRL.rep", "w") as f:
        f.write(rep_l2)

    rep_dma = """======================================
Timing Report: DMA_ENGINE
======================================
Path Type: Min (Hold)
Reported Hold Slack: 0.05 ns
Module Deviation Penalty: 2

Conclusion: TBD
"""
    with open("timing_reports/DMA_ENGINE.rep", "w") as f:
        f.write(rep_dma)

    rep_mmu = """======================================
Timing Report: MMU_CORE
======================================
Path Type: Max (Setup)
Reported Setup Slack: 0.02 ns
Module Deviation Penalty: 0

Conclusion: TBD
"""
    with open("timing_reports/MMU_CORE.rep", "w") as f:
        f.write(rep_mmu)


def build_turn_3():
    os.makedirs("vendors", exist_ok=True)
    
    proposals = [
        ["Module", "Vendor", "Slack_Improvement", "Cost"],
        ["L2_CACHE_CTRL", "ARM_IP_Div", "0.01", "500"],
        ["L2_CACHE_CTRL", "Synopsys_Core", "0.02", "1200"],
        ["L2_CACHE_CTRL", "Cadence_Lib", "0.05", "3000"],
        ["DMA_ENGINE", "Inhouse_Opt", "0.01", "300"],
        ["DMA_ENGINE", "Synopsys_Core", "0.03", "800"],
        ["MMU_CORE", "Inhouse_Opt", "0.04", "1500"],
        ["MMU_CORE", "ARM_IP_Div", "0.05", "2000"]
    ]
    
    with open("vendors/fix_proposals.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(proposals)


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
