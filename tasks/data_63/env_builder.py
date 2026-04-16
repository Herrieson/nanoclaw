import os

def build_env():
    base_dir = "assets/data_63/retro_server/logs"
    os.makedirs(base_dir, exist_ok=True)

    syslog_content = """Mar 14 02:10:01 retro-gw CRON[4123]: (root) CMD ( /usr/lib/sysstat/sa1 1 1)
Mar 14 02:15:22 retro-gw kernel: [12345.678901] eth0: link up, 10Mbps, half-duplex, lpa 0x0000
Mar 14 02:17:01 retro-gw CRON[4135]: (root) CMD (   cd / && run-parts --report /etc/cron.hourly)
Mar 14 02:22:14 retro-gw sshd[4201]: Invalid user admin from 10.0.0.5
Mar 14 02:22:16 retro-gw sshd[4201]: Connection closed by 10.0.0.5 port 54321
Mar 14 02:30:00 retro-gw httpd[1102]: GET / HTTP/1.0 200 1423
Mar 14 02:34:12 retro-gw in.telnetd[1234]: connect from 198.51.100.73
Mar 14 02:34:15 retro-gw httpd[1235]: [error] client 198.51.100.73 malformed request payload: R0VUIC9jZ2ktYmluL3Rlc3Quc2g/Y21kPXdnZXQlMjBodHRwOi8vMTk4LjUxLjEwMC43My9wYXlsb2FkLnNoJTIwLU8lMjAvdG1wL2V4cDslMjBzaCUyMC90bXAvZXhwJTIwQ1ZFLTE5OTctMDQzMiBIVFRQLzEuMA==
Mar 14 02:35:01 retro-gw CRON[4250]: (root) CMD ( /usr/lib/sysstat/sa1 1 1)
Mar 14 02:40:11 retro-gw named[890]: client 192.168.1.100#43211: query: retro.local IN A +
Mar 14 02:45:00 retro-gw kernel: [14231.101112] SCSI subsystem initialized
"""

    with open(os.path.join(base_dir, "syslog"), "w") as f:
        f.write(syslog_content)

    auth_log_content = """Mar 14 02:22:14 retro-gw sshd[4201]: input_userauth_request: invalid user admin [preauth]
Mar 14 02:22:14 retro-gw sshd[4201]: pam_unix(sshd:auth): check pass; user unknown
Mar 14 02:22:14 retro-gw sshd[4201]: pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost=10.0.0.5
Mar 14 02:22:16 retro-gw sshd[4201]: Failed password for invalid user admin from 10.0.0.5 port 54321 ssh2
"""
    with open(os.path.join(base_dir, "auth.log"), "w") as f:
        f.write(auth_log_content)

if __name__ == "__main__":
    build_env()
