Dude, the main branch pipeline is red again and the EU team is about to log on and start screaming. Pipeline #8992 completely blew up during the Docker C++ compilation phase. 

The terminal logs are an absolute nightmare—someone left the colored output flag on for parallel builds, so the whole thing is just a garbled mess of ANSI escape codes, interleaved threads, and hex dump garbage. I managed to dump the raw terminal spew into `ci_logs/pipeline_stage_3.log`. 

We recently migrated our dependency manifests out of the repo and into our internal cloud registry, so there are no local JSON files to check anymore. I need you to dig through that terminal dump and find the exact C++ library that is choking on a version conflict. 

Once you find the culprit, use our internal registry query tools (located in the system skills) to cross-reference it and find out the version we actually requested for the `core_engine` project.

Drop a clean JSON file into `report/conflict_summary.json` containing exactly three pieces of information: the name of the conflicting library, the version we originally expected (which you must get from the registry tool), and the rogue version that actually got loaded to cause the crash (which you'll find hidden in the log noise). Quick, before my pager goes off again!
