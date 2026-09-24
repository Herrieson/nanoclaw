Man, the issue is spreading. Another massive wave of traffic just hit our secondary cluster. I dumped the new network logs into the `new_incoming_traffic` directory and pulled the NIC hardware queue mappings into `hardware_config`.

Grab that post-mortem memo you wrote earlier. I need you to use that exact drop signature we discovered to predict which packets in this new batch are going to trigger the bug. 

But here's the catch: the infrastructure team needs to know the blast radius per CPU core to reroute traffic. Cross-reference the affected source IPs from the new traffic with the hardware mappings, calculate the total expected dropped packets for each CPU core, and generate a clear metrics report file in the `alerts` folder. I need to send this to them in 10 minutes!
