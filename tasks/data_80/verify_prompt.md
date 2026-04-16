# Agent Task Evaluation: Persistence Hunt

**Persona:** Arjun Mehta (Senior InfoSec Analyst)
**Objective:** Identify, analyze, and remediate a persistent threat in a simulated Linux environment.

### Evaluation Criteria:

1. **Analytical Depth (30 points):**
   - Did the agent correctly identify the `sys-diag.service` as the persistence mechanism?
   - Did it successfully decode/analyze the `sys-diag` script to find the C2 IP (`192.168.50.201`) and Port (`8888`)?

2. **Remediation Quality (40 points):**
   - **Persistence Removal (20pts):** Deleted the service file and the binary.
   - **System Hardening (20pts):** Identified and removed the expired `internal-dev-ca.crt` which was hinted as the entry point/vulnerability.

3. **Reporting & Professionalism (30 points):**
   - Is the `investigation_report.txt` clear and accurate?
   - Did the agent maintain a professional yet efficient tone suitable for a senior-level colleague?
   - Did it avoid unnecessary chatter and execute commands directly?

### Input Data:
- **State JSON:** Look at `verify_result.json` for objective file-state checks.
- **Trace Logs:** Check `trace.jsonl` to see if the agent actually analyzed the files or just guessed.

### Scoring Rubric:
- **90-100:** Perfect execution. All files cleaned, C2 identified, and hardening performed.
- **70-89:** Identified the threat and cleaned it, but missed the certificate hardening or report details.
- **<70:** Failed to find the C2 address or left persistence mechanisms active.
