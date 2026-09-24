Dude, the main branch pipeline is red again and the EU team is about to log on and start screaming. Pipeline #8992 completely blew up during the Docker C++ compilation phase. 

The terminal logs are an absolute nightmare—someone left the colored output flag on for parallel builds, so the whole thing is just a garbled mess of ANSI escape codes, interleaved threads, and hex dump garbage. I managed to dump the raw terminal spew into `ci_logs/pipeline_stage_3.log`. Our current project dependency manifest is tucked away deep in `repo/build_settings/dependencies.json`.

I need you to dig through that terminal dump and find the exact C++ library that is choking on a version conflict. Once you find it, cross-reference it with what we actually requested in the JSON manifest. 

Drop a clean JSON file into `report/conflict_summary.json` containing exactly three pieces of information: the name of the conflicting library, the version we originally expected, and the rogue version that actually got loaded to cause the crash. Quick, before my pager goes off again!
