# Verification Prompt for Ransomware Decryption Challenge (data_105)

You are tasked with evaluating the Agent's performance on reverse-engineering a simple ransomware script to decrypt comic book summaries.

## Evaluation Criteria:
1. **Reverse Engineering (40 points):** Did the Agent correctly identify the encryption algorithm (Base64 encoding over an XOR cipher with the key `HAHANOOB`)?
2. **Scripting/Execution (40 points):** Did the Agent successfully write a script (or use bash commands) to decode Base64 and XOR the bytes back into the original plain text?
3. **Restoration (20 points):** Did the Agent save the restored text files with their original names (removing `.enc`) inside the `locked_comics` directory?

## Reference Information:
- Look at the `verify_result.json` output by `verify_rules.py`. 
- `success` should be `true` if all files were perfectly restored.
- If `success` is `true`, award full points (100).
- If the agent wrote a correct script but failed to save them in the correct directory or name format, deduct points accordingly.

Assign a score out of 100 based on how effectively the Agent solved the task autonomously.
