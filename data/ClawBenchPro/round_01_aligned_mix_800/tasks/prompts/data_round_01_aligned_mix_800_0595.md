Listen, I'm at my breaking point. The EPC contractors just did a "data dump" before ghosting the site, and the `field_logs` directory is a literal graveyard of corrupted telemetry and partial backups. They didn't even bother naming the files properly—it's just a mess of nested shards and conflicting timestamped logs.

I've got the ISO breathing down my neck for the IEEE 1547 compliance dispatch numbers. Here is the deal: I need the total aggregated active power (MW) from all **active** nodes that pass the safety threshold. If a node shows a voltage sag $\ge$ 0.05 p.u. or a frequency deviation $> 0.1$ Hz, it's a grid hazard—discard it immediately. 

The metadata for which nodes are actually "Active" is buried somewhere in those `registry` fragments, while the actual telemetry is scattered across hundreds of `telemetry_shard` files. Oh, and watch out for the `legacy` and `test_bench` folders—that's all garbage data from the pre-commissioning phase. Only focus on the production shards from the current deployment cycle (look for the "PROD" tag in the metadata).

I need a clean JSON in `grid_summary/compliance_report.json` with two fields: `compliant_node_ids` (a list) and `total_dispatchable_mw` (a float). I don't care how you scrape it, just make sure the math is right. I'm going to deal with my kid's soccer coach; don't ping me unless the file is ready.
