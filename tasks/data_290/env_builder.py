import os

def build_env():
    base_dir = "assets/data_290"
    os.makedirs(base_dir, exist_ok=True)
    
    raw_logs_content = """[08:00] Shift start. Note: Remember to check the soil pH for the hydrangeas, they are looking chlorotic. Need to get the pH down to 5.5.
[08:15] Pt-1001 triage. C/O chest pain. Vitals: BP 145/90, Temp 37.2 C, HR 88. 
[08:30] Pt-1002 presented with severe headache. Blood pressure 170/105. T 37.0 C. 
[08:45] Pt-1003 routine follow-up. BP 120/80, Temp 36.8 C. All normal.
[09:00] Call nursery about kids' pickup schedule. 
[09:15] Pt-1004, pediatric. Febrile. BP 110/70. Temp 39.2 C.
[09:30] Pt-1005 triage assessment. BP 165/95. Temp 37.1 C.
[09:45] Need to order more perlite for the raised beds.
[10:00] Pt-1006. C/O nausea. Vitals: Blood pressure 130/85. T 38.6 C.
[10:15] Pt-1007. Stable. BP 160/100, Temp 38.5 C. Note: Borderline, monitor closely.
[10:30] Remind husband to water the tomatoes.
"""
    
    with open(os.path.join(base_dir, "raw_logs.txt"), "w") as f:
        f.write(raw_logs_content)

if __name__ == "__main__":
    build_env()
