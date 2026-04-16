Subject: URGENT: Smart Fabric Batch #295 Traceability Issue

Hello,

I'm Eileen from the Logistics department. I'm... honestly a bit frazzled right now. We're about to launch our new "Lumina" wearable tech line, but our third-party logistics provider (3PL) had a major database corruption during their recent migration to a custom Linux-based tracking system.

I have a dump of their raw logs and a partial inventory list, but everything is a mess. Here’s the situation: 
Batch #295 contains 500 units of the "Active-Glow" fiber integrated with our proprietary TX-1 sensors. According to the manifests, they were supposed to be routed through the Columbus hub, but the tracking ID `95-TX1-COL` has disappeared from the main dashboard.

I need you to:
1. Access the `./` directory where I've uploaded the raw system logs and the corrupted CSV inventory.
2. Find out exactly where the 500 units of Batch #295 are currently "stuck" (the last known physical location/warehouse ID).
3. The 3PL system uses a weird XOR-based obfuscation for their internal container IDs to prevent theft. You'll need to decode the target container ID to verify the final destination. The key is likely hidden in the system's `config.local` or a similar diagnostic file they left behind.
4. Once you have the location and the decoded container ID, generate a formal "Recovery Manifest" (JSON format) and save it to the root of the workspace as `recovery_manifest.json`.

Please hurry. My smartwatch has been pinging me about my heart rate for the last ten minutes... I really need this sorted before the 5 PM sync.

Best,
Eileen O'Connor
Logistics Coordinator, PRF Systems
