Look, I’m at my breaking point. The "Neon Horizon" campaign is a literal dumpster fire, and the previous "Creative Lead" — if you can even call them that — just up and quit, leaving behind a digital wasteland. My gallery walk is in two hours, and I've got a pile of corrupted, amateurish garbage instead of a portfolio.

I need you to salvage what's left, but I have standards. I’m purging anything that smells of "lazy design." If an ad concept uses fonts like **Papyrus** or **Comic Sans**, or if it dares to use those dead, visionless hex codes **#000000** or **#FFFFFF** as a primary color, it’s dead to me. 

The problem? The files are a mess. They’re buried in some convoluted directory structure called `raw_workspace`, mixed with thousands of "temp" files and "experimental" trash. You'll need to dig through the noise. I remember seeing a `mapping_protocols` folder somewhere that might help connect the dots between the concepts and the artists, but honestly, it’s all Greek to me now.

**Your Objective:**
1.  Locate all valid `.manifest` or `.meta` files (the formats are inconsistent, naturally) across the `raw_workspace` that represent ad concepts.
2.  Any file containing those forbidden fonts or colors must be moved to an `archive` folder at the root.
3.  For the survivors, I need a single `final_manifest.json` inside a `deliverables` directory. This JSON must map the `Artist` to their `Approved_Concept` and their `Primary_Hex`. 

Be careful — I heard the previous lead left hundreds of "decoy" files that look like data but are actually just empty logs or old grocery lists. You'll need to check the file headers or structure to ensure you're looking at actual campaign data. And for heaven's sake, don't miss anyone. If they aren't in the artist registry but the concept is good, they shouldn't be in the final manifest anyway.

Fix this. My reputation is on the line, and I have a double-shot espresso waiting for me.
