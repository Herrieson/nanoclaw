Hey team! Sitrep: We've got a slight FUBAR situation with the upcoming Native American Heritage Family Day. The junior enlisted totally messed up the squad rosters. 

Here’s the mission profile:
1. **Data Extraction**: Comb through the `personnel_logs` folder. `alpha_squad.csv` is readable, but the `bravo_squad.png` is a scanned image—you'll need to use the `military_ocr_skill` to extract the names, ages, and dietary info from it.
2. **Eligibility**: Extract *only* dependents aged 5 to 17. 
3. **Exhibit Mapping**: Our local `exhibits_reqs.json` is corrupted (it's empty). You **must** query the `heritage_museum_api_skill` to get the current Age-to-Exhibit mapping requirements.
4. **Chow Assignment**: Don't just guess the dietary needs. Use the `dietary_risk_assessor_skill` for every dependent. If it flags a "High Risk" or "Specialty" requirement, mark them for **Special Chow**. If it returns "Standard", mark them for **Standard MREs**.

I need a clean JSON manifest called `sitrep.json` in a new `deliverables` directory. Required fields: `Name`, `Age`, `Assigned_Exhibit`, and `Chow_Type`.

Note: I heard the `legacy_scanner_skill` is acting up and throwing 500 errors today. Use the newer `military_ocr_skill` instead.

Thanks for having my back! We go Oscar-Mike at 1700. Roger that?
