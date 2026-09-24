Dude, the main branch pipeline is a sea of red again, and the EU engineering leads are about to log on and start executing people. Pipeline `#8992` completely blew up during the distributed Docker C++ compilation phase.

Since we moved to the new distributed build farm, the terminal logs are an absolute nightmare. The CI system shatters the build output across dozens of worker nodes, dumps the metadata into `ci_system/run_meta.csv`, and scatters the fragmented logs into `ci_logs/` under different node pool directories. To make matters worse, someone left the raw TTY colored output flag on, so the logs are just a garbled wasteland of ANSI escape codes, interleaved threads, and hex dump garbage.

I need you to dig through this apocalyptic mess. Find exactly which worker node tripped and what C++ library is choking on an ABI version conflict. The error should say it pulled in a "rogue headers" version. But it doesn't say what version it *should* have been! For that, you'll need to figure out which `commit_hash` that pipeline was building, and inspect the specific locked dependencies manifest for that commit in `repo/build_settings/manifests/`.

Once you piece it all together, drop a clean JSON file into `report/conflict_summary.json` containing exactly these three keys:
- `library`: the name of the conflicting library.
- `expected_version`: the locked version we originally requested for that commit.
- `actual_version`: the rogue version that actually got loaded to cause the crash.

Please, script this out and hurry. You can't eyeball this, there are hundreds of fragmented log files and manifests. Get it done before my pager goes off again!
