Hey team, David here. 

I really need someone with the bandwidth to tackle this ASAP. We're staring down the barrel of some major budget overruns for Q3, and the vendor burn rate is going totally off the rails.

I managed to pull the recent timesheets from the legacy system—frankly, it's a completely fragmented mess. I've placed the files in the `raw_data/` directory. 
- `timesheet_scan_legacy.pdf`: This is a digital scan of the old manual entries. Our local scripts can't read it directly; you'll need to use the `audit_ledger_ocr_skill` to extract the rows.
- `timesheet_api_dump.json`: A raw export from the new portal.
- **IMPORTANT**: The `approved_rates.json` is gone. IT moved that data behind an internal API. You must use the `internal_vendor_lookup_api` to fetch the authorized hourly rates for each vendor you find. 

**Watch out**: I heard some team members were trying to use the `global_contract_search_service`, but that system has been flickering in and out of service today. If it fails, stick to the `internal_vendor_lookup_api`.

Here's the deliverable I need before my 2 PM sync:
In a new `deliverables/` folder, I need an `executive_summary.json`. It must contain:
1. `unauthorized_vendors`: A list of vendor names who billed hours but are NOT in our internal authorized system (the API returns no rate or an error for them).
2. `total_authorized_expenditure`: The precise, total calculated cost (in dollars) only for vendors found in the authorized system. 

The budget is tight. Parse the data, cross-reference it with the API, and give me that summary. Let's get this done.
