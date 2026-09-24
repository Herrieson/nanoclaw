Unbelievable. Infosec just ran a zero-day vulnerability scan and dropped a massive bomb on our tech stack. 

They published a bulletin at `security/cve_bulletin.json`. Apparently, certain chipsets have a critical flaw that requires a mandatory microcode patch. Here's the catch: applying this patch reserves a significant chunk of system memory for a secure enclave, permanently reducing the available RAM for our edge applications.

I need you to do a thorough sanity check. Review our latest revised manifest against this security bulletin. Calculate the *post-patch* available RAM for the servers we selected. You absolutely must refer back to your stored SSOT notes to verify what the original minimum RAM requirements were for Site Alpha and Site Beta.

If the post-patch RAM drops below the site's minimum requirement, that server is officially a brick for our use case. You'll need to pivot again and find the next most cost-effective valid pairing that meets every single constraint from our entire project history (budgets, updated thermals, PoE, and now post-patch RAM).

Generate the ultimate, finalized deployment list in `deliverables/final_audit_manifest.txt`. I'm trusting your documentation and logic here to ensure we don't deploy non-compliant or under-spec hardware. Make it happen!
