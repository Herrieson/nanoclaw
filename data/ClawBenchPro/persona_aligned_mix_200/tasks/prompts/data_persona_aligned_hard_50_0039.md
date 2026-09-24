Damn it, the whole datacenter just had a massive cascading power trip and wiped out half our cluster! Everything is completely on fire and the business side is screaming about the downtime.

I’ve pulled the recovered `dmesg` logs from all 200 nodes and dumped them into the `logs/` directory tree. Most of them are entirely useless noise—watchdog timeouts, network interface drops, or secondary OOM kills. However, there is exactly **one** node that suffered a fatal, unrecoverable kernel panic due to a `NULL pointer dereference` strictly during an `ext4_orphan_cleanup` operation. 

I need you to dig through the debris immediately:
1. Find that specific kernel crash log. Extract the exact instruction pointer (RIP) hex address where the kernel died from the register dump (just the raw hex address, e.g., `ffffffff...`).
2. Identify the block device name that caused this specific crash (it will be something like `nvme...` mentioned in the exact same panic log).
3. I used `dd` and `hexdump -C` to pull the raw 4KB superblocks of *every* attached drive in the cluster. They are sitting in the `disk_dumps/` directory. Find the dump file that perfectly matches the failing device.
4. In that specific drive's hex dump, hunt down the Ext4 filesystem magic signature `53 EF`. Right after those two bytes, I had a custom kernel patch that forcibly flushed the first 5 orphan inode numbers consecutively as an emergency debugging measure before the crash happened. They are stored as standard 32-bit little-endian integers.

*Note:* `hexdump -C` wraps lines every 16 bytes. Don't write a lazy line-by-line regex that fails when the magic bytes or the integers straddle a line boundary! Reconstruct the byte stream first if you have to. Also, beware of decoy `53 EF` bytes in the other drives' garbage data!

Extract the RIP address and those 5 orphan inode numbers (convert them back to standard base-10 integers). Put them into a file named `recovery_plan.json` under the keys `rip_address` (as a string) and `orphan_inodes` (as an array of integers). Do not give me a lecture on filesystem theory, just output the JSON so my automated scripts can begin the surgical reconstruction!
