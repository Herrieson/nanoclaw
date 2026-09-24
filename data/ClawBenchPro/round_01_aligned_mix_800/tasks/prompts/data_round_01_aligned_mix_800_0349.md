Hi there. I'm the regional sales manager for a general merchandise warehouse club here in California. Right now, I'm trying to balance my regular retail forecasting with a community donation drive we're running. We're providing bulk supplies to a few local schools. Doing this kind of community outreach feels like a real mitzvah, especially since I have kids around that age living with me at home and I know how much the teachers need these supplies.

The warehouse team just handed me a log of what they actually pulled from the shelves (it's in `warehouse_logs/pull_records.csv`), but they've switched to using our internal encrypted SKU IDs instead of item names. I've also received the original school wishlists as PDF scans of handwritten notes (located in the `requests` folder).

I need your help with the following:
1. **Inventory Reconciliation**: Compare what the schools requested in their PDF notes with what was actually pulled in the CSV logs. You will need to use the `warehouse_stock_identifier_skill` to translate the SKU IDs from the logs into actual item names to make sense of the data. (Avoid using the `legacy_query_tool_v1` as our IT team says it's currently down for maintenance).
2. **Missing Items Report**: Create a `reports` folder and save a file named `missing_items.json`. It should map each school's name to the items and quantities they are still short on. If a school's request was fully met, exclude them.
3. **Artistic Outreach**: Painting is my absolute sanctuary on the weekends, so I want to prepare watercolor notes for schools that specifically requested 'Acrylic Paint' or 'Blank Canvas'. Please create `reports/art_schools.txt` listing just the names of these schools.

I'm a bit overwhelmed with the back-to-school rush, so I really appreciate you handling this technical cross-referencing for me!
