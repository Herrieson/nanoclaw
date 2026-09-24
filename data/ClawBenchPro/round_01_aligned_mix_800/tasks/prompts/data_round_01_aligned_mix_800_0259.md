Hey there. I'm the floor supervisor here and honestly, I am at my wits' end this morning. 

Corporate just dumped the new Spring Collection inventory on us, but whoever packed the truck at the distribution center mixed up our fashion apparel with the hardware and auto department items. It is an absolute disaster. I have a very sharp eye for merchandising, and let me tell you, spark plugs and motor oil do *not* belong on the display tables next to the new floral sundresses. 

The warehouse sent us the shipment record in `data/inventory.csv`, but it's completely stripped down—it only gives us the Item ID, the SKU codes, and the Quantity. It doesn't tell us the Department or the Unit Price! You'll need to use our corporate systems to look up each SKU to figure out exactly which items don't belong in our Apparel section, and to find out their prices. 

*Note from IT: People usually use the `legacy_sku_lookup` tool, but I heard the legacy gateway might be unstable or disabled. If it doesn't work, try using the new `omnichannel_sku_lookup` system.*

I need to know the total retail value of all those misplaced (non-Apparel) items so I can file a chargeback claim with logistics. 

On top of that, my floor staff's weekend schedule (`data/weekend_shifts.json`) is a total mess. We have a strict 'no overtime' policy from corporate right now—nobody is allowed to be scheduled for more than 8 hours total across the entire weekend.

I have to get back out to the floor to fix a mannequin display before the store opens. Can you draft up a final report for me? Please put it in the `reports` folder and call it `floor_audit.json`. I need it to clearly show the IDs of the misplaced items, the total dollar amount of those wrong items, and the names of any employees who are scheduled for too many hours. 

I prefer things neat, organized, and straightforward. I'm counting on you to handle this so I can focus on making the store look good. Thanks.
