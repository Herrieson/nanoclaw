Listen, I have exactly ten minutes before I have to leave to pick up my toddler from daycare, and I do not have the patience for incompetence today. I'm running on fumes, and I just walked in to find that the weekend pharmacy temps left our inventory logs an absolute disaster. It's completely disorganized, and cleanliness and order are non-negotiable in a medical setting! 

Instead of a single neat log, they used two different faulty barcode scanners and dumped hundreds of fragments into the `logs/weekend_dumps/` directory. Some output JSON, some output CSV. Half the files lost power midway and are physically corrupted. If a file is broken, or if an individual record is missing any of the required fields (`code`, `batch`, `exp`, `qty`) or contains blank values, throw it in the trash. I only care about intact data!

Worse, the scanners only logged the internal drug codes! You have to cross-reference them with the master registry to know what they actually are. IT dumped a bunch of old reference registries in the `reference/` folder, but only use the registry file that has the word 'approved' in its filename. Ignore the decoys!

Here is what you must do immediately with the valid records:

1. **Quarantine**: Anything with an expiration year of 2023 or older is garbage (e.g., `2023-12-31` is expired). Save these records to `deliverables/quarantine.csv` with the headers exactly as `code,name,batch,exp,qty` (where `name` is the actual drug name from the registry). Sort the rows by `code` ascending, then `batch` ascending.

2. **CII Alerts**: For the UNEXPIRED meds, I need a strictly separated alert list for Schedule II controlled substances so I can personally secure them in the locked safe. Save this to `deliverables/cii_alerts.csv` with the same columns and sorting as above, but only for unexpired drugs marked as "CII" in the registry.

3. **Valid Tally**: For the remaining meds (UNEXPIRED and NON-CII), they are safe to dispense. Tally up the total quantity available for each drug name, and save it as `deliverables/valid_tally.json` (format must be exactly `{"Drug Name": TotalQty, ...}`).

The `deliverables` folder must contain exactly these three files and nothing else. I speak quickly, and I expect you to act quickly. Write a script, clean this up, and do not leave any loose ends. Get to work!
