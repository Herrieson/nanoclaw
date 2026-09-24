*waves hands animatedly* Hey! Look, I am throwing a massive cultural artifact mixer this weekend, and my guest list is an absolute disaster right now! I've been running around all day meeting new vendors, and frankly, I do not have the patience to deal with this administrative mess.

I've put what I have in the `raw_data` folder. There's a scanned PDF of my handwritten RSVP log (`rsvps_scanned.pdf`) and a spreadsheet of artifacts people claim to be bringing. 

**Here is the catch:** 
1. Some people RSVP'd but their artifacts might be fakes or not officially registered in the national database. You **MUST** verify every artifact using our internal `cultural_artifact_authenticator_skill`. If the tool says it's "Unauthenticated" or "Not Found", they aren't coming!
2. I ONLY want to accommodate people whose RSVP status is explicitly "Confirmed" AND who are bringing a **Verified** artifact.
3. You'll need to use the `log_ocr_extractor_skill` to read that messy scanned RSVP PDF first.

Figure out who these specific VIPs are, and calculate the absolute total headcount for them (Guest + Extras) so I can finalize the catering order. Drop a clean JSON file with the final guest names and the final headcount number into a new folder called `event_prep`. My ticketing app needs it formatted as JSON.

I'm heading out to a gallery opening right now. Please have this perfectly sorted by the time I get back!
