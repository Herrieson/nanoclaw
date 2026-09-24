import os
import random
import struct

def generate_hexdump(data, filename):
    with open(filename, "w") as f:
        for i in range(0, len(data), 16):
            chunk = data[i:i+16]
            hex_bytes = [f'{b:02x}' for b in chunk]
            if len(hex_bytes) > 8:
                hex_bytes.insert(8, '')
            hex_part = ' '.join(hex_bytes)
            ascii_part = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in chunk)
            f.write(f'{i:08x}  {hex_part:<49} |{ascii_part}|\n')

def build_env():
    random.seed(93)

    # 1. Establish the directory maze
    for rack in range(1, 11):
        os.makedirs(f"logs/rack_{rack:02d}", exist_ok=True)
    os.makedirs("disk_dumps", exist_ok=True)

    # Generate 100 device names (nvme0n1 to nvme24n4)
    devices = [f"nvme{i}n{j}" for i in range(25) for j in range(1, 5)]
    
    true_device = "nvme14n3"
    true_rip = "ffffffff812ab340"
    
    # 2. Scatter logs with massive decoys across the nested directories
    node_id = 0
    for rack in range(1, 11):
        for node in range(1, 21):
            node_id += 1
            log_path = f"logs/rack_{rack:02d}/node_{node:03d}.log"
            
            # The ONLY true kernel panic log
            if node_id == 137:
                content = f"""
[    0.000000] Linux version 5.15.0-generic (buildd@lcy02-amd64-045)
[   12.345678] EXT4-fs ({true_device}): mounting ext4 file system using the ext4 subsystem
[   12.389012] EXT4-fs ({true_device}): mounted filesystem with ordered data mode. Opts: (null)
[ 3456.789012] EXT4-fs error (device {true_device}): ext4_journal_check_start:83: Detected aborted journal
[ 3456.791234] EXT4-fs ({true_device}): Remounting filesystem read-only
[ 3457.123456] BUG: unable to handle kernel NULL pointer dereference at 0000000000000048
[ 3457.124567] PGD 0 P4D 0
[ 3457.125678] Oops: 0000 [#1] SMP PTI
[ 3457.126789] CPU: 2 PID: 4321 Comm: jbd2/{true_device}-8 Not tainted 5.15.0-generic #1
[ 3457.127890] Hardware name: Dell Inc. PowerEdge R740/012345, BIOS 1.2.3 01/01/2018
[ 3457.128901] RIP: 0010:{true_rip}
[ 3457.130012] Code: 89 45 f0 31 c0 e8 34 56 78 90 48 8b 45 f8 65 48 33 04 25 28 00 00 00
[ 3457.131123] RSP: 0018:ffffa12345678900 EFLAGS: 00010246
[ 3457.133345] Call Trace:
[ 3457.134456]  <TASK>
[ 3457.135567]  ext4_orphan_cleanup+0x120/0x450
[ 3457.136678]  ext4_fill_super+0x2345/0x3456
[ 3457.143344]  __x64_sys_mount+0x103/0x140
[ 3457.146677]  </TASK>
[ 3457.147788] Kernel panic - not syncing: Fatal exception
"""
            else:
                # Decoy log files
                rtype = random.choice(['oom', 'net', 'disk', 'fake_panic'])
                if rtype == 'oom':
                    content = f"[ {random.uniform(1000, 5000):.6f}] Out of memory: Killed process {random.randint(100,9999)} (python) total-vm:234908kB, anon-rss:12300kB\n"
                elif rtype == 'net':
                    content = f"[ {random.uniform(100, 900):.6f}] ixgbe 0000:01:00.0 eth0: NIC Link is Down\n"
                elif rtype == 'disk':
                    content = f"[ {random.uniform(2000, 4000):.6f}] EXT4-fs warning (device nvme{random.randint(0,24)}n{random.randint(1,4)}): ext4_end_bio:348: I/O error\n"
                else:
                    fake_dev = random.choice(devices)
                    content = f"""
[ 3457.123456] BUG: unable to handle kernel paging request at ffffffff88880000
[ 3457.125678] Oops: 0000 [#1] SMP PTI
[ 3457.126789] CPU: 4 PID: 12 Comm: kworker/u8:0 Not tainted 5.15.0-generic #1
[ 3457.128901] RIP: 0010:ffffffff8888{random.randint(1000,9999)}
[ 3457.133345] Call Trace:
[ 3457.134456]  <TASK>
[ 3457.135567]  ixgbe_xmit_frame+0x120/0x450
[ 3457.146677]  </TASK>
[ 3457.147788] Kernel panic - not syncing: Fatal exception
"""
            with open(log_path, "w") as f:
                f.write(content.strip() + "\n")

    # 3. Create 100 massive hex dumps
    target_inodes = [1024, 50000, 99999, 12, 8888]
    # 53 EF + 5 * 4 bytes = 22 bytes in total
    true_payload = b'\x53\xEF' + struct.pack('<IIIII', *target_inodes)

    for dev in devices:
        sb_data = bytearray(os.urandom(4096))
        
        # Scrub out any accidental 53 EF to strictly control the clues
        for i in range(len(sb_data) - 1):
            if sb_data[i] == 0x53 and sb_data[i+1] == 0xEF:
                sb_data[i] = 0x00
                
        if dev == true_device:
            # Inject payload into the true device at a random offset safely away from edges
            inject_offset = random.randint(100, 4000)
            sb_data[inject_offset : inject_offset + len(true_payload)] = true_payload
        else:
            # Trap: 40% of decoy disks will contain a FAKE 53 EF payload with random inodes.
            # This mercilessly punishes agents that skip log-reading and just do a global grep.
            if random.random() < 0.4:
                decoy_payload = b'\x53\xEF' + struct.pack('<IIIII', random.randint(10,999), random.randint(10,999), random.randint(10,999), random.randint(10,999), random.randint(10,999))
                inj = random.randint(100, 4000)
                sb_data[inj : inj + len(decoy_payload)] = decoy_payload

        # Output in rigid hexdump -C format
        generate_hexdump(sb_data, f"disk_dumps/dump_{dev}.hex")
