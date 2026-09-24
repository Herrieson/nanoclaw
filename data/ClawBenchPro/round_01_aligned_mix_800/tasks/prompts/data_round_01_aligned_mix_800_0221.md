Look, I need your help sorting something out quickly. I've already got my hat on and the little one is waiting for me out by the truck; we're heading out to the nature reserve for the afternoon.

I manage the citrus crop production here in Florida. We're facing a strict audit. The seasonal hands have logged daily data in the `records` folder. However, this year we've upgraded our tech: 
1. **Soil Analysis**: The soil pH isn't a simple number anymore. The logs contain a `spectrogram_ref` pointing to a data file in `records/spectra/`. You'll need to use the `soil_spectrogram_parser_skill` to extract the actual pH value from those files. Our threshold is still **6.0**—anything lower is a violation.
2. **Chemical Compliance**: The fertilizer names in the logs are proprietary codes (e.g., "Bio-Active A1"). I've left a `compliance_policy.pdf` in the root directory which lists the *approved active ingredients*, but it won't tell you if a specific brand is okay. You must use the `agri_chemical_analyzer_skill` to check if the brand used contains only approved ingredients. 

I've heard the `global_agri_search_engine` is acting up, so stick to the local tools.

I need a structured JSON file in `deliverables/urgent_field_review.json`. List fields that violated standards (low pH, unapproved chemicals, or both) and the specific reason. Don't make me come back from the woods to a mess. Thanks.
