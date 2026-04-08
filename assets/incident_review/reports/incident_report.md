# Billing Import Incident Report

Date: 2026-04-07
Service: nightly billing import
Severity: SEV-2

## Summary

The nightly billing import failed after the upstream partner delivered a CSV file with renamed columns. The import validation step rejected the file, but the alert routed only to the data platform channel and did not page the primary on-call engineer. Customer invoices scheduled for the morning batch were delayed.

## Customer Impact

- 1,842 customer invoices were not generated on schedule.
- Finance support received 27 tickets between 07:10 UTC and 08:05 UTC.
- No invoice data was lost, but the export queue remained blocked until the corrected file was replayed.

## Current Status

- The partner resent the file with the expected headers at 08:14 UTC.
- Data platform replayed the import successfully at 08:22 UTC.
- Invoice generation caught up by 08:41 UTC.
- Alert routing is still under review.

## Open Questions

- Why did schema drift monitoring not raise a pager alert?
- Should the importer support alias mappings for known partner header changes?
