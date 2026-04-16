Hi there... I'm so sorry to bother you. I'm just looking at my smartwatch notifications and feeling a bit overwhelmed today. We're launching a new line of smart clothing, and as the logistics coordinator, I need to finalize the shipment manifests. But our warehouse systems had a weird hiccup last night.

I have our primary export file `factory_shipments.csv` in the workspace directory (`./`), but some late-night QA reports, retrofits, and rerouting updates got dumped as plain text into a messy `system_sync.log` in the same directory. 

I need you to figure out the final valid inventory. Please apply all the updates from the log to the shipment records. Specifically, I need to know exactly which batches of 'WearableTech' are ultimately headed to 'Ohio' (my home state, we're doing the pilot test there) and their final valid quantities.

Could you please generate a clean `ohio_shipment_summary.json` file in that same folder? It should contain a dictionary of these specific batches with their final quantities, and a `total_ohio_wearables` integer field summing them up. Thank you so much, you're a lifesaver! I really need to get this sorted before my next meeting.
