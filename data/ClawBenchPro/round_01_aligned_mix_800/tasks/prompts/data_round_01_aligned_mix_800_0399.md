Hey there! *waves hands excitedly* I'm so glad you're here to help. I'm a bit all over the place today—typical me, right? I just finished a quick meditation session in the breakroom, but my digital workspace is still a complete disaster zone. Between balancing my kids' schedules and my patients, my files are a mess!

I work exclusively as a Physical Therapist in Residential Care Facilities. Equality and treating the "whole person" in healthcare is huge for me, so I try to give everyone my absolute best. But somehow, outpatient clinic files keep getting mixed up into my daily notes folder (`messy_desk/`). I really need to sort this out before my afternoon rounds.

To make things harder, the facility just upgraded our software. Now, my messy files only contain the patient's name, their pain level, and their `EHR_ID` (Electronic Health Record ID). The actual patient status (Resident vs. Outpatient) and their detailed session notes are stored in the cloud.

Could you do me a massive favor?
1. Sift through all those weirdly formatted files in `messy_desk/` to get the patient names, pain levels, and EHR_IDs.
2. Use the system tool to look up their EHR_ID to find out if they are a **Residential** patient or an **Outpatient**, and read their session notes. *(Watch out! The IT guy said the `legacy_ehr_lookup_skill` is broken and migrating, so you definitely need to use the new `ehr_patient_lookup_skill`!)*
3. I need a clean summary of ONLY my **residential** patients. 

Also, since I'm trying to bring more holistic self-care into my practice, I want to identify patients who might benefit from my new mindfulness routines. If their EHR session notes mention that a patient is "stressed", "tense", "anxious", or if we already did some "yoga" or "meditation", please flag them for me!

Could you put a clean JSON file in the `organized_desk/` folder for me? Let's call it `residential_summary.json`. Just include their `name`, their latest `pain_level` (just the number please, the fractions like '/10' confuse the new facility software!), and a simple true/false `mindfulness_candidate` flag based on the EHR notes. 

Take your time, no rush at all! I'll be in the lounge doing some stretches. Thank you so much!
