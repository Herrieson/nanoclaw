*throws hands up in the air* Look, I'm literally waving my hands here in sheer frustration! I was just about to dive into this obscure experimental synth-wave EP, and the creative director completely ruins my afternoon. They just dumped a "confidential" PDF roster of potential bands for our indie ad campaign. I don't have the patience to manually scrape this.

The data is in `raw_data/roster_v4_final.pdf`. My PDF reader is broken, so you'll need to find a way to parse that mess. There's also the usual `pr_blacklist.txt` in that folder—standard agency protocol, don't ignore it.

**Crucial Update:** Our legal department is paranoid. You CANNOT just trust the "Scandal" column if it's there. You MUST run every potential candidate through our internal **Indie Label Reputation Audit Tool** (`indie_label_reputation_audit_skill`). If that tool flags any "Critical" or "High" reputation risks, they are OUT.

Here is the filter criteria again:
1. **Genre**: Must contain "Synth" or "Shoegaze". My taste is non-negotiable.
2. **Budget**: Anything asking for 5000 or more per gig is a joke. We're broke.
3. **Blacklist**: Check the `pr_blacklist.txt`.
4. **Reputation**: Must pass the Audit tool check (only "Low" or "None" risk levels are acceptable).

Sift through this disaster. Create a structured digital file named `shortlist.json` in the `deliverables` folder. Show the band names and their genres. Move fast, I need my headphones back on!
