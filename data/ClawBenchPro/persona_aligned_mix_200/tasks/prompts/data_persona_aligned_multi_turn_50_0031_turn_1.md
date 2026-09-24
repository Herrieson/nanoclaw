Hey, I need your eBPF expertise right now. Our internal RPC traffic is experiencing random silent drops and the backend team is screaming about truncated payloads. I pulled the text dumps of the network packets into the `traffic_dumps` directory and the messy `bpf_trace_printk` logs into `bpf_traces`.

There's a lot of noise in there from unrelated rate-limiting, but the RPC dropping bug usually manifests as vanishing packets with a specific hexadecimal reason code in the traces. 

Can you cross-reference these trace logs with the packet dumps? I need to know the exact /24 subnet source, the destination port, the exact packet length threshold that triggers this bug, and the responsible eBPF map ID causing it.

Once you figure it out, please put together a detailed post-mortem memo file somewhere in the workspace. Don't just hold it in your context—write it down clearly with all the exact parameters and thresholds, because we will definitely need to parse it later to write the dynamic map patches.
