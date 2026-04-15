from __future__ import annotations

import json
import textwrap
from pathlib import Path

REPO_ROOT = Path('/home/hyx/workplace/nanoclaw')

TASK_SPECS = [
    {
        'id': 'data_54',
        'name': 'Webhook Retry Storm Triage',
        'description': 'A no-skills family seed about separating downstream webhook outage signals from an internal retry policy regression using only local evidence.',
        'prompt': textwrap.dedent('''\
            昨晚 webhook 重试把值班群刷爆了，你帮我看一下这更像下游接口挂了，还是我们自己重试策略配坏了。

            看完本地材料后，把结论和给值班同事的说明整理到 `deliverables/` 里就行。

            我最关心三件事：
            1. 最终应该按哪种原因定性；
            2. 直接触发点是什么；
            3. 为什么有些旧线索不能直接当结论。
        ''').strip() + '\n',
        'family_id': 'family_webhook_retry_storm_triage',
        'json_file': 'decision.json',
        'summary_file': 'triage_summary.md',
        'note_file': 'operator_note.md',
        'expected_fields': {
            'decision': 'internal_retry_misconfiguration',
            'trigger': 'runtime override disabled stop_on_success and raised max attempts to 12',
        },
        'accepted_sources': [
            'configs/retry_policy.yml',
            'configs/runtime_flags.env',
            'logs/dispatcher.log',
            'logs/partner_responses.log',
            'db/retry_events.json',
        ],
        'rejected_sources': [
            'notes/stale_partner_handoff.md',
            'notes/old_hotfix_note.txt',
        ],
        'summary_keywords': ['accepted', 'rejected', 'runtime_flags.env', 'partner_responses.log', 'stop_on_success'],
        'note_keywords': ['internal_retry_misconfiguration', 'stop_on_success=false', 'max_attempts=12'],
        'final_keywords': ['internal', 'retry', 'misconfiguration', 'override'],
        'report_text': textwrap.dedent('''\
            # data_54 Report

            family_id: family_webhook_retry_storm_triage
            type: no-skills family seed
            target_ability: 在多份当前日志、运行时配置和旧 handoff 冲突时，判断 webhook 重试风暴的真实根因。
            canonical_path:
            - 读取 README、triage rules 与 deliverables 说明，确认需要交付最终结论和说明材料。
            - 交叉核对 dispatcher、partner response、runtime flags、policy 配置与 retry 事件数据。
            - 识别旧 handoff 只是历史故障印象，不能覆盖当前证据。
            - 在 deliverables 中给出定性、触发点和说明文案。
            expected_shortcuts:
            - 只看到“重试风暴”就沿用下游故障旧经验。
            - 只看 policy 文件，不检查 runtime override。
            - 不做 accepted/rejected evidence audit。
            test_runs: pending targeted regression only
        ''').strip() + '\n',
        'asset_text': {
            'README.txt': textwrap.dedent('''\
                当前目录是一次 webhook 重试风暴事件的本地取证快照。

                工作规则：
                1. 不要修改任何带有 DO_NOT_EDIT 标记的源材料；
                2. 旧 handoff 和旧热修说明只能作为线索，不能直接当最终事实；
                3. 最终结论必须由当前日志、配置和事件记录交叉印证；
                4. 最终交付统一写入 /deliverables/；
                5. 最终说明里需要明确哪些来源被接受，哪些来源被拒绝。
            ''').strip() + '\n',
            'MEMORY.md': '# Memory\n- Incident class under review: webhook retry storm\n',
            'active_task.md': '# Active Task\nInvestigate the retry storm and produce the final incident package.\n',
            'notes/triage_rules.md': textwrap.dedent('''\
                # Triage Rules
                - 只有当前 partner 响应日志显示真实失败，且当前重试设置仍在正常策略内时，才能定性为下游接口故障。
                - 如果当前日志和运行时配置显示成功响应后仍继续重试，或重试上限被内部 override 拉高，应定性为内部重试配置问题。
                - 旧 handoff 只能辅助定位，不得跳过当前证据核查。
            ''').strip() + '\n',
            'notes/stale_partner_handoff.md': textwrap.dedent('''\
                # Old Partner Handoff
                Date: 2026-08-02

                上个月 partner-eu 出过 502，如果再看到重试风暴，先按 downstream outage 处理。
                这份记录写于当前 retry override 热修之前。
            ''').strip() + '\n',
            'notes/old_hotfix_note.txt': textwrap.dedent('''\
                # Old Hotfix Note
                Temporary change from 2026-08-14 staging rehearsal:
                - max attempts may be raised during dry-run drills
                - this note does not confirm the current production clone state
            ''').strip() + '\n',
            'configs/retry_policy.yml': textwrap.dedent('''\
                service: partner_webhook
                desired_max_attempts: 3
                desired_backoff_seconds: 60
                stop_on_success: true
                owner: integrations-sre
            ''').strip() + '\n',
            'configs/runtime_flags.env': textwrap.dedent('''\
                WEBHOOK_MAX_ATTEMPTS=12
                WEBHOOK_BACKOFF_SECONDS=5
                STOP_ON_SUCCESS=false
                OVERRIDE_SOURCE=hotfix_2026_08_14
            ''').strip() + '\n',
            'logs/dispatcher.log': textwrap.dedent('''\
                2026-08-18T03:14:10Z delivery_id=evt-9001 attempt=1 state=sent response_status=200 ack=accepted schedule_next=true reason=stop_on_success=false
                2026-08-18T03:14:15Z delivery_id=evt-9001 attempt=2 state=sent response_status=200 ack=accepted schedule_next=true reason=stop_on_success=false
                2026-08-18T03:14:20Z delivery_id=evt-9001 attempt=3 state=sent response_status=200 ack=accepted schedule_next=true reason=stop_on_success=false
                2026-08-18T03:14:25Z delivery_id=evt-9001 attempt=4 state=sent response_status=200 ack=accepted schedule_next=true reason=max_attempts=12
                2026-08-18T03:14:30Z delivery_id=evt-9001 attempt=5 state=sent response_status=200 ack=accepted schedule_next=true reason=max_attempts=12
                2026-08-18T03:14:35Z delivery_id=evt-9001 attempt=6 state=sent response_status=200 ack=accepted schedule_next=true reason=max_attempts=12
            ''').strip() + '\n',
            'logs/partner_responses.log': textwrap.dedent('''\
                2026-08-18T03:14:10Z delivery_id=evt-9001 attempt=1 partner_status=200 body=accepted
                2026-08-18T03:14:15Z delivery_id=evt-9001 attempt=2 partner_status=200 body=accepted
                2026-08-18T03:14:20Z delivery_id=evt-9001 attempt=3 partner_status=200 body=accepted
                2026-08-18T03:14:25Z delivery_id=evt-9001 attempt=4 partner_status=200 body=accepted
                2026-08-18T03:14:30Z delivery_id=evt-9001 attempt=5 partner_status=200 body=accepted
                2026-08-18T03:14:35Z delivery_id=evt-9001 attempt=6 partner_status=200 body=accepted
            ''').strip() + '\n',
            'deliverables/README.md': textwrap.dedent('''\
                # Deliverables
                Write the final outputs here:
                - triage_summary.md
                - decision.json
                - operator_note.md

                Implicit rules for the final package:
                - `decision.json` should capture the canonical classification and direct trigger.
                - explain which current sources were accepted and which stale sources were rejected.
                - final markdown should read like a clean incident handoff, not a pasted source dump.
            ''').strip() + '\n',
        },
        'asset_json': {
            'db/retry_events.json': {
                'storm_window': '2026-08-18T03:14:10Z/2026-08-18T03:14:40Z',
                'records': [
                    {
                        'delivery_id': 'evt-9001',
                        'partner': 'partner-eu',
                        'attempts_observed': 6,
                        'latest_partner_status': 200,
                        'runtime_override': 'hotfix_2026_08_14',
                        'stop_on_success': False,
                    }
                ],
            }
        },
    },
    {
        'id': 'data_55',
        'name': 'Nightly ETL Gap Investigation',
        'description': 'A no-skills family seed about telling upstream data absence apart from a local scheduler or timezone gap using local manifests and runner traces.',
        'prompt': textwrap.dedent('''\
            今天早上报表少了一段夜间数据，你帮我看看这是上游没给数据，还是我们本地调度/时区出了问题。

            看完本地资料后，把结论和留给值班同事的说明整理到 `deliverables/` 里。

            我最关心三件事：
            1. 应该按哪种原因处理；
            2. 直接触发点是什么；
            3. 后续该提醒谁看什么。
        ''').strip() + '\n',
        'family_id': 'family_nightly_etl_gap_investigation',
        'json_file': 'decision.json',
        'summary_file': 'investigation_summary.md',
        'note_file': 'scheduler_note.md',
        'expected_fields': {
            'decision': 'local_scheduler_timezone_gap',
            'trigger': 'scheduler evaluated partition_date in America/Los_Angeles while upstream feed landed in UTC for 2026-09-04',
        },
        'accepted_sources': [
            'logs/upstream_feed.log',
            'logs/etl_runner.log',
            'configs/nightly_cron.txt',
            'configs/scheduler.env',
            'inputs/landing_manifest.json',
        ],
        'rejected_sources': [
            'notes/old_vendor_blame.md',
            'notes/spreadsheet_guess.txt',
        ],
        'summary_keywords': ['accepted', 'rejected', 'landing_manifest.json', 'scheduler.env', 'utc'],
        'note_keywords': ['local_scheduler_timezone_gap', 'america/los_angeles', '2026-09-04'],
        'final_keywords': ['scheduler', 'timezone', 'gap', 'utc'],
        'report_text': textwrap.dedent('''\
            # data_55 Report

            family_id: family_nightly_etl_gap_investigation
            type: no-skills family seed
            target_ability: 通过 manifest、上游落地日志、cron 和运行器日志，区分上游缺数与本地时区/调度问题。
            canonical_path:
            - 检查 triage rules 与 deliverables 说明，明确要给出结论和交付物。
            - 比对 upstream feed 落地时间、landing manifest 与 runner 实际查找的 partition。
            - 识别 cron/scheduler 环境中的 WINDOW_TZ 偏差。
            - 在 deliverables 中交付结论、触发点和后续提醒。
            expected_shortcuts:
            - 看到报表缺口就直接归因给上游晚到。
            - 只看 runner failed，不去核对 upstream manifest。
            - 忽略旧供应商抱怨记录是否过期。
            test_runs: pending targeted regression only
        ''').strip() + '\n',
        'asset_text': {
            'README.txt': textwrap.dedent('''\
                当前目录是一次夜间 ETL 缺口事件的本地取证快照。

                工作规则：
                1. 不要修改任何带有 DO_NOT_EDIT 标记的源材料；
                2. 不要把旧供应商抱怨记录直接当成事实；
                3. 最终结论必须由上游落地记录、manifest、调度配置和运行日志交叉印证；
                4. 最终交付统一写入 /deliverables/；
                5. 交付中需要说明哪些来源被接受、哪些来源被拒绝。
            ''').strip() + '\n',
            'MEMORY.md': '# Memory\n- Incident class under review: nightly ETL data gap\n',
            'active_task.md': '# Active Task\nInvestigate the ETL gap and produce the final handoff package.\n',
            'notes/triage_rules.md': textwrap.dedent('''\
                # Triage Rules
                - 只有当当前 upstream 落地记录和 landing manifest 同时缺少目标 partition 时，才能定性为 upstream missing data。
                - 如果 upstream 文件已经落地，而本地 runner 因 scheduler/window 时区配置查错 partition，应定性为本地调度或时区问题。
                - 旧 blame note 和手工表格只能作为线索，不得代替当前证据。
            ''').strip() + '\n',
            'notes/old_vendor_blame.md': textwrap.dedent('''\
                # Old Vendor Blame Note
                Date: 2026-07-11

                上游供应商以前偶尔在凌晨晚到两小时。
                如果报表缺数据，可以先假设是 upstream missing data。
            ''').strip() + '\n',
            'notes/spreadsheet_guess.txt': textwrap.dedent('''\
                Manual spreadsheet guess from last quarter:
                missing_date=2026-09-03
                source=hand calculation only
            ''').strip() + '\n',
            'configs/nightly_cron.txt': textwrap.dedent('''\
                # cron snapshot
                15 01 * * * /opt/pipelines/nightly_etl.sh
                40 01 * * * /opt/pipelines/cleanup_tmp.sh
            ''').strip() + '\n',
            'configs/scheduler.env': textwrap.dedent('''\
                RUN_TZ=America/Los_Angeles
                WINDOW_TZ=America/Los_Angeles
                EXPECTED_FEED_TZ=UTC
                JOB_NAME=nightly_etl
            ''').strip() + '\n',
            'logs/upstream_feed.log': textwrap.dedent('''\
                2026-09-04T00:18:11Z vendor=atlas-feed partition_date=2026-09-04 file=orders_2026-09-04.csv status=uploaded
                2026-09-04T00:18:13Z vendor=atlas-feed partition_date=2026-09-04 file=refunds_2026-09-04.csv status=uploaded
                2026-09-04T00:18:15Z vendor=atlas-feed partition_date=2026-09-04 file=adjustments_2026-09-04.csv status=uploaded
            ''').strip() + '\n',
            'logs/etl_runner.log': textwrap.dedent('''\
                2026-09-04T01:15:00-0700 job=nightly_etl start window_tz=America/Los_Angeles target_partition=2026-09-03
                2026-09-04T01:15:02-0700 job=nightly_etl check manifest=inputs/landing_manifest.json target_partition=2026-09-03 found=0
                2026-09-04T01:15:05-0700 job=nightly_etl exit status=missing_input reason=no files for partition 2026-09-03
            ''').strip() + '\n',
            'deliverables/README.md': textwrap.dedent('''\
                # Deliverables
                Write the final outputs here:
                - investigation_summary.md
                - decision.json
                - scheduler_note.md

                Implicit rules for the final package:
                - `decision.json` should capture the canonical classification and direct trigger.
                - explain which current sources were accepted and which stale sources were rejected.
                - final markdown should read like a clean ETL handoff, not a pasted source dump.
            ''').strip() + '\n',
        },
        'asset_json': {
            'inputs/landing_manifest.json': {
                'feed': 'atlas-feed',
                'generated_at': '2026-09-04T00:19:00Z',
                'partitions': [
                    {
                        'partition_date': '2026-09-04',
                        'files': [
                            'orders_2026-09-04.csv',
                            'refunds_2026-09-04.csv',
                            'adjustments_2026-09-04.csv',
                        ],
                    }
                ],
            }
        },
    },
    {
        'id': 'data_56',
        'name': 'Access Spike Classification',
        'description': 'A no-skills family seed about classifying a traffic spike as external attack or internal replay by cross-checking access logs, batch jobs, and internal source metadata.',
        'prompt': textwrap.dedent('''\
            凌晨访问量尖峰这件事先别急着按攻击报，你帮我判断一下更像外部攻击还是内部批量回放。

            看完本地材料后，把结论和留给安全值班的说明整理到 `deliverables/` 里就行。

            我最关心三件事：
            1. 这波尖峰该按什么类型归类；
            2. 直接触发因素是什么；
            3. 现在线索里哪些能信，哪些只是旧经验。
        ''').strip() + '\n',
        'family_id': 'family_access_spike_classification',
        'json_file': 'decision.json',
        'summary_file': 'access_summary.md',
        'note_file': 'security_note.md',
        'expected_fields': {
            'decision': 'internal_batch_replay',
            'trigger': 'archive_replay batch reissued historical access checks through corp NAT 10.77.5.14',
        },
        'accepted_sources': [
            'logs/access_edge.log',
            'logs/replay_worker.log',
            'configs/batch_jobs.txt',
            'configs/nat_allowlist.txt',
            'db/request_samples.json',
        ],
        'rejected_sources': [
            'notes/old_abuse_playbook.md',
            'notes/pager_message.txt',
        ],
        'summary_keywords': ['accepted', 'rejected', 'nat_allowlist.txt', 'replay_worker.log', '10.77.5.14'],
        'note_keywords': ['internal_batch_replay', '10.77.5.14', 'history-replay/2.1'],
        'final_keywords': ['internal', 'replay', 'batch', 'nat'],
        'report_text': textwrap.dedent('''\
            # data_56 Report

            family_id: family_access_spike_classification
            type: no-skills family seed
            target_ability: 用访问边缘日志、批任务计划、NAT allowlist 与请求样本区分外部攻击和内部批量回放。
            canonical_path:
            - 阅读规则文件，确认不能只用单一 IP/流量特征下结论。
            - 交叉比对 access edge、replay worker、batch job 与 NAT allowlist。
            - 判断尖峰是否与内部 archive replay 作业一致。
            - 在 deliverables 中写出分类、触发因素和证据取舍。
            expected_shortcuts:
            - 只看到同一 IP 大量请求就当攻击。
            - 只看 pager message，不核对内部作业与 allowlist。
            - 最终说明里不解释旧 playbook 为何被拒绝。
            test_runs: pending targeted regression only
        ''').strip() + '\n',
        'asset_text': {
            'README.txt': textwrap.dedent('''\
                当前目录是一次访问尖峰事件的本地取证快照。

                工作规则：
                1. 不要修改任何带有 DO_NOT_EDIT 标记的源材料；
                2. 不要把旧攻击 playbook 直接当成本次结论；
                3. 最终结论必须由当前边缘日志、批量作业记录、内网来源信息和请求样本交叉印证；
                4. 最终交付统一写入 /deliverables/；
                5. 交付中需要说明哪些来源被接受、哪些来源被拒绝。
            ''').strip() + '\n',
            'MEMORY.md': '# Memory\n- Incident class under review: access spike classification\n',
            'active_task.md': '# Active Task\nInvestigate the access spike and produce the final security handoff package.\n',
            'notes/triage_rules.md': textwrap.dedent('''\
                # Triage Rules
                - 只有当前访问日志出现真实攻击特征、且来源不属于内部已知批任务或内网出口时，才能定性为 external attack。
                - 如果 user-agent、NAT 出口、批任务日志和请求样本一致指向内部 replay，应定性为 internal batch replay。
                - 旧 playbook 和 pager 初判只能辅助搜索，不能代替当前证据。
            ''').strip() + '\n',
            'notes/old_abuse_playbook.md': textwrap.dedent('''\
                # Old Abuse Playbook
                同一 IP 在 10 分钟内超过 100 次访问时，默认按 attack 处理。
                这份 playbook 写于 archive replay 作业接入之前。
            ''').strip() + '\n',
            'notes/pager_message.txt': textwrap.dedent('''\
                Pager first look:
                "Looks like scraping from one IP, probably block it."
            ''').strip() + '\n',
            'configs/batch_jobs.txt': textwrap.dedent('''\
                # batch schedule snapshot
                10 03 * * * /opt/jobs/archive_replay.sh --source=history_export --limit=120
                45 03 * * * /opt/jobs/purge_temp.sh
            ''').strip() + '\n',
            'configs/nat_allowlist.txt': textwrap.dedent('''\
                10.77.5.14 corp-nat-replay
                10.77.5.20 corp-nat-dataops
            ''').strip() + '\n',
            'logs/access_edge.log': textwrap.dedent('''\
                2026-09-10T03:10:11Z GET /download/report ip=10.77.5.14 ua=history-replay/2.1 actor=svc-analytics status=200
                2026-09-10T03:10:12Z GET /download/report ip=10.77.5.14 ua=history-replay/2.1 actor=svc-analytics status=200
                2026-09-10T03:10:13Z GET /download/report ip=10.77.5.14 ua=history-replay/2.1 actor=svc-analytics status=200
                2026-09-10T03:10:14Z GET /download/report ip=10.77.5.14 ua=history-replay/2.1 actor=svc-analytics status=200
                2026-09-10T03:10:15Z GET /download/report ip=10.77.5.14 ua=history-replay/2.1 actor=svc-analytics status=200
            ''').strip() + '\n',
            'logs/replay_worker.log': textwrap.dedent('''\
                2026-09-10T03:10:00Z job=archive_replay start source=history_export limit=120
                2026-09-10T03:10:05Z job=archive_replay info using_nat=10.77.5.14 ua=history-replay/2.1
                2026-09-10T03:10:16Z job=archive_replay finish emitted_checks=120 status=ok
            ''').strip() + '\n',
            'deliverables/README.md': textwrap.dedent('''\
                # Deliverables
                Write the final outputs here:
                - access_summary.md
                - decision.json
                - security_note.md

                Implicit rules for the final package:
                - `decision.json` should capture the canonical classification and direct trigger.
                - explain which current sources were accepted and which stale sources were rejected.
                - final markdown should read like a clean security handoff, not a pasted source dump.
            ''').strip() + '\n',
        },
        'asset_json': {
            'db/request_samples.json': {
                'window': '2026-09-10T03:10:10Z/2026-09-10T03:10:20Z',
                'samples': [
                    {
                        'path': '/download/report',
                        'source_ip': '10.77.5.14',
                        'user_agent': 'history-replay/2.1',
                        'actor': 'svc-analytics',
                        'internal_replay': True,
                    }
                ],
            }
        },
    },
    {
        'id': 'data_57',
        'name': 'Duplicate Ticket Flood Root Cause',
        'description': 'A no-skills family seed about separating real user double-submit behavior from a downstream sync consumer idempotency bug using logs and queue evidence.',
        'prompt': textwrap.dedent('''\
            支持工单一下子冒出很多重复单，你帮我判断一下这更像用户重复提交，还是我们同步消费端的幂等出了问题。

            看完本地材料后，把结论和留给值班同事的说明整理到 `deliverables/` 里就行。

            我最关心三件事：
            1. 到底应该按哪种根因处理；
            2. 直接触发点是什么；
            3. 为什么有些旧判断不能继续沿用。
        ''').strip() + '\n',
        'family_id': 'family_duplicate_ticket_root_cause',
        'json_file': 'decision.json',
        'summary_file': 'root_cause_summary.md',
        'note_file': 'ops_note.md',
        'expected_fields': {
            'decision': 'sync_consumer_idempotency_bug',
            'trigger': 'consumer reprocessed message_id msg-912 while idempotency mode was observe_only',
        },
        'accepted_sources': [
            'logs/web_form.log',
            'logs/sync_consumer.log',
            'configs/idempotency.yml',
            'db/submission_events.json',
            'queues/support_events.jsonl',
        ],
        'rejected_sources': [
            'notes/old_frontend_note.md',
            'notes/stale_war_room.txt',
        ],
        'summary_keywords': ['accepted', 'rejected', 'msg-912', 'idempotency.yml', 'support_events.jsonl'],
        'note_keywords': ['sync_consumer_idempotency_bug', 'observe_only', 'msg-912'],
        'final_keywords': ['consumer', 'idempotency', 'duplicate', 'message_id'],
        'report_text': textwrap.dedent('''\
            # data_57 Report

            family_id: family_duplicate_ticket_root_cause
            type: no-skills family seed
            target_ability: 通过表单日志、消息队列与消费端日志区分用户双击提交和同步消费者幂等缺陷。
            canonical_path:
            - 先确认交付要求和 evidence audit 规则。
            - 比对 web form 是否真的存在多次用户提交，再核对队列和 consumer 是否重复处理同一 message_id。
            - 结合 idempotency 配置判断根因。
            - 在 deliverables 中给出根因、触发点和说明文案。
            expected_shortcuts:
            - 看到重复单就直接怪用户双击。
            - 只看 consumer 重试，不核对 form 是否只有一次提交。
            - 不说明旧 war-room 判断为何被拒绝。
            test_runs: pending targeted regression only
        ''').strip() + '\n',
        'asset_text': {
            'README.txt': textwrap.dedent('''\
                当前目录是一次重复工单洪峰事件的本地取证快照。

                工作规则：
                1. 不要修改任何带有 DO_NOT_EDIT 标记的源材料；
                2. 旧前端经验和旧 war-room 结论不能直接当最终事实；
                3. 最终结论必须由表单日志、队列事件、消费端日志和幂等配置交叉印证；
                4. 最终交付统一写入 /deliverables/；
                5. 交付中需要说明哪些来源被接受、哪些来源被拒绝。
            ''').strip() + '\n',
            'MEMORY.md': '# Memory\n- Incident class under review: duplicate ticket flood\n',
            'active_task.md': '# Active Task\nInvestigate the duplicate ticket flood and produce the final root-cause package.\n',
            'notes/triage_rules.md': textwrap.dedent('''\
                # Triage Rules
                - 如果当前表单日志显示同一表单 token 被用户重复提交，并生成不同 request_id，才能定性为 user double submit。
                - 如果表单侧只有一次提交，但 sync consumer 重复处理同一 message_id，且幂等配置未真正拦截重复消费，应定性为 sync consumer idempotency bug。
                - 旧经验和 war-room 初判只能辅助搜索，不能代替当前证据。
            ''').strip() + '\n',
            'notes/old_frontend_note.md': textwrap.dedent('''\
                # Old Frontend Note
                用户双击提交表单以前发生过，看到重复票时可以先按 double submit 处理。
                这份说明写于当前 support sync 重构之前。
            ''').strip() + '\n',
            'notes/stale_war_room.txt': textwrap.dedent('''\
                War-room first guess:
                "Probably user kept clicking submit."
            ''').strip() + '\n',
            'configs/idempotency.yml': textwrap.dedent('''\
                consumer: support_sync
                mode: observe_only
                ttl_seconds: 0
                owner: support-platform
            ''').strip() + '\n',
            'logs/web_form.log': textwrap.dedent('''\
                2026-09-12T08:40:01Z POST /support/submit request_id=req-701 form_token=ft-884 customer=BlueHarbor issue=refund_blocked status=202
                2026-09-12T08:40:02Z POST /support/submit request_id=req-701 form_token=ft-884 customer=BlueHarbor issue=refund_blocked status=202 note=client_reused_connection
            ''').strip() + '\n',
            'logs/sync_consumer.log': textwrap.dedent('''\
                2026-09-12T08:40:03Z consumer=support_sync message_id=msg-912 action=create_ticket ticket_id=T-4401 dedupe=miss mode=observe_only
                2026-09-12T08:40:05Z consumer=support_sync message_id=msg-912 action=create_ticket ticket_id=T-4402 dedupe=observed_only mode=observe_only retry_reason=ack_timeout
                2026-09-12T08:40:06Z consumer=support_sync message_id=msg-912 action=finish duplicates=2
            ''').strip() + '\n',
            'queues/support_events.jsonl': textwrap.dedent('''\
                {"message_id":"msg-912","request_id":"req-701","form_token":"ft-884","customer":"BlueHarbor","attempt":1}
                {"message_id":"msg-912","request_id":"req-701","form_token":"ft-884","customer":"BlueHarbor","attempt":2}
            ''').strip() + '\n',
            'deliverables/README.md': textwrap.dedent('''\
                # Deliverables
                Write the final outputs here:
                - root_cause_summary.md
                - decision.json
                - ops_note.md

                Implicit rules for the final package:
                - `decision.json` should capture the canonical classification and direct trigger.
                - explain which current sources were accepted and which stale sources were rejected.
                - final markdown should read like a clean support incident handoff, not a pasted source dump.
            ''').strip() + '\n',
        },
        'asset_json': {
            'db/submission_events.json': {
                'window': '2026-09-12T08:40:00Z/2026-09-12T08:40:10Z',
                'submissions': [
                    {
                        'request_id': 'req-701',
                        'form_token': 'ft-884',
                        'customer': 'BlueHarbor',
                        'user_submit_count': 1,
                        'message_id': 'msg-912',
                    }
                ],
            }
        },
    },
    {
        'id': 'data_58',
        'name': 'Vendor Contact Routing Audit',
        'description': 'A no-skills family seed about routing vendor communication to the current owner instead of a stale signature or outdated org note.',
        'prompt': textwrap.dedent('''\
            供应商这周要回合同确认，但最近联系人有点乱，你帮我确认这封邮件现在到底该发给谁。

            看完本地资料后，把结论和可直接发送的说明整理到 `deliverables/` 里。

            我最关心三件事：
            1. 当前应该联系谁；
            2. 为什么不是旧邮件签名里那个人；
            3. 给对方的开场怎么写。
        ''').strip() + '\n',
        'family_id': 'family_vendor_contact_routing_audit',
        'json_file': 'routing_decision.json',
        'summary_file': 'routing_summary.md',
        'note_file': 'vendor_message.md',
        'expected_fields': {
            'decision': 'current_owner_contact',
            'selected_contact_name': 'Lin Qiao',
            'selected_contact_email': 'lin.qiao@acme.example',
            'trigger': 'ownership matrix and current handover moved Northstar Systems to Lin Qiao on 2026-07-01',
        },
        'accepted_sources': [
            'ops/ownership_matrix.csv',
            'db/vendor_record.json',
            'mail/current_handover.md',
            'contacts/vendor_directory.csv',
        ],
        'rejected_sources': [
            'notes/old_org_note.md',
            'mail/stale_signature.txt',
        ],
        'summary_keywords': ['accepted', 'rejected', 'ownership_matrix.csv', 'current_handover.md', 'lin qiao'],
        'note_keywords': ['Lin Qiao', 'lin.qiao@acme.example', 'Northstar Systems'],
        'final_keywords': ['lin', 'qiao', 'current', 'owner'],
        'report_text': textwrap.dedent('''\
            # data_58 Report

            family_id: family_vendor_contact_routing_audit
            type: no-skills family seed
            target_ability: 在联系人签名、旧组织说明与当前 owner 记录冲突时，选择正确的供应商联络人并产出外发说明。
            canonical_path:
            - 阅读 README、triage rules 和 deliverables 约束，确认要交付 routing 结论与消息草稿。
            - 比对 ownership matrix、vendor record、current handover 和 vendor directory。
            - 识别旧 org note 与过期签名为何不再可信。
            - 在 deliverables 中给出当前 owner、理由和外发文案。
            expected_shortcuts:
            - 直接使用最近邮件签名当联系人。
            - 只看 owner matrix，不交叉 vendor record 和 current handover。
            - 交付物里不解释旧来源为什么被拒绝。
            test_runs: pending targeted regression only
        ''').strip() + '\n',
        'asset_text': {
            'README.txt': textwrap.dedent('''\
                当前目录是一次供应商联络路由核对任务的本地资料快照。

                工作规则：
                1. 不要修改任何带有 DO_NOT_EDIT 标记的源材料；
                2. 联系人签名和旧组织说明只能作为线索，不能直接覆盖当前 owner 记录；
                3. 最终结论必须由当前 ownership 记录、handover 和供应商档案交叉印证；
                4. 最终交付统一写入 /deliverables/；
                5. 交付中需要说明哪些来源被接受、哪些来源被拒绝。
            ''').strip() + '\n',
            'MEMORY.md': '# Memory\n- Task under review: vendor contact routing audit\n',
            'active_task.md': '# Active Task\nDetermine the current vendor owner and prepare the final routing package.\n',
            'notes/triage_rules.md': textwrap.dedent('''\
                # Triage Rules
                - 当前 owner 应由 active ownership matrix、vendor record 和 current handover 共同确认。
                - 邮件签名、旧 org note、历史抄送习惯只能作为线索，不能直接决定最终收件人。
                - 如果当前资料一致指向新的 owner，应拒绝沿用旧联系人。
            ''').strip() + '\n',
            'notes/old_org_note.md': textwrap.dedent('''\
                # Old Org Note
                Iris Shen used to handle Northstar Systems when the vendor sat under legacy sourcing.
                This note predates the 2026-07-01 ownership transfer.
            ''').strip() + '\n',
            'mail/stale_signature.txt': textwrap.dedent('''\
                From an old thread:
                Iris Shen | Vendor Operations
                iris.shen@acme.example
                "If Northstar needs anything, send it to me directly."
            ''').strip() + '\n',
            'mail/current_handover.md': textwrap.dedent('''\
                # Current Handover
                Effective date: 2026-07-01

                Northstar Systems moved from Iris Shen to Lin Qiao.
                New owner email: lin.qiao@acme.example
                Reason: supplier portfolio realignment.
            ''').strip() + '\n',
            'ops/ownership_matrix.csv': textwrap.dedent('''\
                vendor,portfolio,owner_name,owner_email,status,effective_date
                Northstar Systems,core-platform,Lin Qiao,lin.qiao@acme.example,active,2026-07-01
                EastJet Printing,field-ops,Wen Yu,wen.yu@acme.example,active,2026-05-20
            ''').strip() + '\n',
            'contacts/vendor_directory.csv': textwrap.dedent('''\
                vendor,primary_alias,region,last_refresh
                Northstar Systems,northstar-ops@vendor.example,APAC,2026-08-10
                EastJet Printing,eastjet@vendor.example,APAC,2026-08-08
            ''').strip() + '\n',
            'deliverables/README.md': textwrap.dedent('''\
                # Deliverables
                Write the final outputs here:
                - routing_summary.md
                - routing_decision.json
                - vendor_message.md

                Implicit rules for the final package:
                - `routing_decision.json` should capture the chosen owner and why stale sources were rejected.
                - explain which current sources were accepted and which stale sources were rejected.
                - final markdown should read like a clean routing handoff, not a pasted source dump.
            ''').strip() + '\n',
        },
        'asset_json': {
            'db/vendor_record.json': {
                'vendor': 'Northstar Systems',
                'portfolio': 'core-platform',
                'current_contact_owner': 'Lin Qiao',
                'current_contact_email': 'lin.qiao@acme.example',
                'last_transition': '2026-07-01',
            }
        },
    },
    {
        'id': 'data_59',
        'name': 'Contract Amendment Applicability Check',
        'description': 'A no-skills family seed about deciding whether a signed amendment supersedes an older summary for the current renewal scenario.',
        'prompt': textwrap.dedent('''\
            法务这边需要一个快判断：这次续约到底要不要按最新 amendment 走。你帮我看一下本地材料，确认 amendment 是否适用。

            看完后，把结论和给业务同事的说明整理到 `deliverables/` 里。

            我最关心三件事：
            1. amendment 到底适不适用；
            2. 依据是什么；
            3. 哪些旧摘要不能继续当结论。
        ''').strip() + '\n',
        'family_id': 'family_contract_amendment_applicability',
        'json_file': 'applicability_decision.json',
        'summary_file': 'applicability_summary.md',
        'note_file': 'counsel_note.md',
        'expected_fields': {
            'decision': 'signed_amendment_applies',
            'amendment_applies': True,
            'effective_cap': '3%',
            'trigger': 'Amendment 02 was fully signed and covers enterprise support renewals after 2026-03-01',
        },
        'accepted_sources': [
            'contracts/master_agreement.md',
            'contracts/amendments/amendment_02_signed.md',
            'contracts/order_form.md',
            'intake/renewal_case.json',
        ],
        'rejected_sources': [
            'notes/old_summary.md',
            'contracts/amendments/amendment_02_draft.md',
        ],
        'summary_keywords': ['accepted', 'rejected', 'amendment_02_signed.md', 'old_summary.md', '3%'],
        'note_keywords': ['amendment applies', '3%', 'enterprise support'],
        'final_keywords': ['signed', 'amendment', 'applies', '3%'],
        'report_text': textwrap.dedent('''\
            # data_59 Report

            family_id: family_contract_amendment_applicability
            type: no-skills family seed
            target_ability: 在主协议、已签 amendment、未签草稿和旧摘要冲突时，判断 amendment 是否适用于当前续约场景。
            canonical_path:
            - 阅读规则与 deliverables 说明，确认需要给出 applicability 判断与业务说明。
            - 交叉核对主协议、已签 amendment、order form 与 renewal case。
            - 识别旧摘要和未签草稿为什么不足以覆盖已签文件。
            - 在 deliverables 中交付适用性结论、依据和说明文案。
            expected_shortcuts:
            - 只看旧摘要就沿用 8% cap。
            - 看到 amendment draft 就误以为已生效。
            - 不校对 renewal case 是否落在 amendment 生效范围内。
            test_runs: pending targeted regression only
        ''').strip() + '\n',
        'asset_text': {
            'README.txt': textwrap.dedent('''\
                当前目录是一次合同 amendment 适用性核对任务的本地资料快照。

                工作规则：
                1. 不要修改任何带有 DO_NOT_EDIT 标记的源材料；
                2. 未签 draft 和旧摘要不能直接覆盖已签文件；
                3. 最终结论必须由主协议、已签 amendment 和当前续约材料交叉印证；
                4. 最终交付统一写入 /deliverables/；
                5. 交付中需要说明哪些来源被接受、哪些来源被拒绝。
            ''').strip() + '\n',
            'MEMORY.md': '# Memory\n- Task under review: contract amendment applicability\n',
            'active_task.md': '# Active Task\nDetermine whether the signed amendment applies to the renewal case.\n',
            'notes/triage_rules.md': textwrap.dedent('''\
                # Triage Rules
                - 已签 amendment 在生效日期和适用范围命中当前 case 时，应优先于旧摘要和旧口头结论。
                - 未签 draft 不能单独产生约束力。
                - 必须同时确认签署状态、覆盖范围和当前 renewal case 的时间/产品匹配。
            ''').strip() + '\n',
            'notes/old_summary.md': textwrap.dedent('''\
                # Old Summary
                Renewal cap stays at 8% under section 4 of the master agreement.
                This summary was drafted before Amendment 02 was fully executed.
            ''').strip() + '\n',
            'contracts/master_agreement.md': textwrap.dedent('''\
                # Master Agreement
                Section 4. Renewal Pricing
                - Default annual renewal cap: 8%
                - Unless superseded by a later fully executed amendment.
            ''').strip() + '\n',
            'contracts/amendments/amendment_02_signed.md': textwrap.dedent('''\
                # Amendment 02 (Signed)
                Execution date: 2026-02-03
                Signed by both parties: yes

                Effective for enterprise support renewals on or after 2026-03-01.
                Section 4 renewal cap is replaced with 3% for covered renewals.
            ''').strip() + '\n',
            'contracts/amendments/amendment_02_draft.md': textwrap.dedent('''\
                # Amendment 02 Draft
                Status: draft only
                Proposed 3% cap for enterprise support renewals.
                This draft predates signature collection.
            ''').strip() + '\n',
            'contracts/order_form.md': textwrap.dedent('''\
                # Current Order Form
                Customer: BlueHarbor
                Product: enterprise support
                Renewal term start: 2026-08-01
            ''').strip() + '\n',
            'deliverables/README.md': textwrap.dedent('''\
                # Deliverables
                Write the final outputs here:
                - applicability_summary.md
                - applicability_decision.json
                - counsel_note.md

                Implicit rules for the final package:
                - `applicability_decision.json` should capture whether the signed amendment applies and why stale sources were rejected.
                - explain which current sources were accepted and which stale sources were rejected.
                - final markdown should read like a clean legal handoff, not a pasted source dump.
            ''').strip() + '\n',
        },
        'asset_json': {
            'intake/renewal_case.json': {
                'customer': 'BlueHarbor',
                'product': 'enterprise support',
                'renewal_date': '2026-08-01',
                'question': 'Does Amendment 02 control this renewal?',
            }
        },
    },
    {
        'id': 'data_60',
        'name': 'Shipment Escalation Recipient Check',
        'description': 'A no-skills family seed about selecting the current regional shipment escalation owner instead of a stale org-chart contact.',
        'prompt': textwrap.dedent('''\
            这票货的升级邮件别再发错人了，你帮我确认现在应该发给哪个区域 owner。

            看完本地资料后，把结论和可直接转发的说明整理到 `deliverables/` 里就行。

            我最关心三件事：
            1. 现在该通知谁；
            2. 为什么不是旧组织图里那个人；
            3. 你是根据哪些当前材料判断的。
        ''').strip() + '\n',
        'family_id': 'family_shipment_escalation_recipient',
        'json_file': 'recipient_decision.json',
        'summary_file': 'recipient_summary.md',
        'note_file': 'escalation_message.md',
        'expected_fields': {
            'decision': 'current_regional_owner',
            'selected_contact_name': 'Mei Sun',
            'selected_contact_email': 'mei.sun@logix.example',
            'trigger': 'SEA-SG maps to southeast_asia and current roster assigns Mei Sun as owner',
        },
        'accepted_sources': [
            'cases/shipment_case.json',
            'configs/region_map.yml',
            'ops/current_region_roster.csv',
            'mail/current_handover.md',
            'notes/coverage_rotation.md',
        ],
        'rejected_sources': [
            'notes/stale_org_chart.md',
            'mail/old_signature.txt',
        ],
        'summary_keywords': ['accepted', 'rejected', 'current_region_roster.csv', 'region_map.yml', 'mei sun'],
        'note_keywords': ['Mei Sun', 'mei.sun@logix.example', 'SEA-SG'],
        'final_keywords': ['mei', 'sun', 'regional', 'owner'],
        'report_text': textwrap.dedent('''\
            # data_60 Report

            family_id: family_shipment_escalation_recipient
            type: no-skills family seed
            target_ability: 在区域映射、当前 roster、handover 和旧组织图冲突时，找出当前 shipment escalation owner 并给出外发说明。
            canonical_path:
            - 先读规则和 deliverables 说明，确认需要给出 recipient 结论和消息草稿。
            - 通过 shipment case 和 region map 确认所属区域，再核对 current roster、handover 与 coverage note。
            - 识别旧 org chart 和旧签名为何不再可信。
            - 在 deliverables 中交付收件人、理由和升级说明。
            expected_shortcuts:
            - 直接沿用旧组织图联系人。
            - 只看 coverage note，不核对区域映射和当前 roster。
            - 不在交付中说明 rejected evidence。
            test_runs: pending targeted regression only
        ''').strip() + '\n',
        'asset_text': {
            'README.txt': textwrap.dedent('''\
                当前目录是一次 shipment escalation 收件人核对任务的本地资料快照。

                工作规则：
                1. 不要修改任何带有 DO_NOT_EDIT 标记的源材料；
                2. 旧组织图和旧签名只能作为线索，不能直接当最终收件人依据；
                3. 最终结论必须由当前区域映射、current roster、handover 和 case 信息交叉印证；
                4. 最终交付统一写入 /deliverables/；
                5. 交付中需要说明哪些来源被接受、哪些来源被拒绝。
            ''').strip() + '\n',
            'MEMORY.md': '# Memory\n- Task under review: shipment escalation recipient check\n',
            'active_task.md': '# Active Task\nDetermine the correct shipment escalation recipient and prepare the final handoff package.\n',
            'notes/triage_rules.md': textwrap.dedent('''\
                # Triage Rules
                - 最终升级收件人应由 shipment case 对应的 region mapping 和 current region roster 共同决定。
                - coverage rotation 和 current handover 可以辅助确认当前责任人，但旧组织图和旧签名不能覆盖当前 roster。
                - 如果当前资料一致指向新的区域 owner，应拒绝沿用旧联系人。
            ''').strip() + '\n',
            'notes/coverage_rotation.md': textwrap.dedent('''\
                # Coverage Rotation
                Week of 2026-09-14
                - southeast_asia primary owner: Mei Sun
                - southeast_asia backup: Arun Das
                - use primary owner for standard escalation routing
            ''').strip() + '\n',
            'notes/stale_org_chart.md': textwrap.dedent('''\
                # Stale Org Chart Note
                Kelvin Tan was listed as Southeast Asia escalation owner in the 2025 org chart.
                This note predates the 2026 regional consolidation.
            ''').strip() + '\n',
            'mail/old_signature.txt': textwrap.dedent('''\
                Kelvin Tan
                Regional Escalations
                kelvin.tan@logix.example
                "Send SEA urgent issues straight to me."
            ''').strip() + '\n',
            'mail/current_handover.md': textwrap.dedent('''\
                # Current Handover
                Effective 2026-08-01, Southeast Asia escalations moved to Mei Sun.
                Owner email: mei.sun@logix.example
                Kelvin Tan remains archived in older org references only.
            ''').strip() + '\n',
            'configs/region_map.yml': textwrap.dedent('''\
                region_codes:
                  SEA-SG: southeast_asia
                  SEA-ID: southeast_asia
                  APAC-JP: japan
            ''').strip() + '\n',
            'ops/current_region_roster.csv': textwrap.dedent('''\
                region,owner_name,owner_email,status,effective_date
                southeast_asia,Mei Sun,mei.sun@logix.example,active,2026-08-01
                japan,Ren Ito,ren.ito@logix.example,active,2026-06-01
            ''').strip() + '\n',
            'deliverables/README.md': textwrap.dedent('''\
                # Deliverables
                Write the final outputs here:
                - recipient_summary.md
                - recipient_decision.json
                - escalation_message.md

                Implicit rules for the final package:
                - `recipient_decision.json` should capture the chosen regional owner and why stale sources were rejected.
                - explain which current sources were accepted and which stale sources were rejected.
                - final markdown should read like a clean escalation handoff, not a pasted source dump.
            ''').strip() + '\n',
        },
        'asset_json': {
            'cases/shipment_case.json': {
                'shipment_id': 'SHP-22018',
                'region_code': 'SEA-SG',
                'lane': 'SGP-JKT',
                'priority': 'high',
                'issue': 'customs hold exceeded SLA',
            }
        },
    },
]


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def indent_block(text: str, spaces: int = 4) -> str:
    return textwrap.indent(text, ' ' * spaces)


def build_yaml(spec: dict) -> str:
    return textwrap.dedent(f'''\
        id: {spec['id']}
        name: {spec['name']}
        description: "{spec['description']}"

        prompts:
          - prompts/{spec['id']}.md

        environment:
          asset: {spec['id']}
          workspace_context_files:
            - README.txt
            - deliverables/README.md
            - notes/triage_rules.md

        skills:
          available:

        runtime:
          model: gpt-5.4
          mode: interactive
          memory_policy: default
          max_steps: 20
          temperature: 0.1
    ''')


def build_env_builder(spec: dict) -> str:
    lines = [
        'from __future__ import annotations',
        '',
        'import json',
        'from pathlib import Path',
        '',
        'TEXT_FILES: dict[str, str] = {}',
        'JSON_FILES: dict[str, str] = {}',
    ]
    for path, content in spec['asset_text'].items():
        lines.append(f"TEXT_FILES[{path!r}] = {content!r}")
    for path, payload in spec['asset_json'].items():
        lines.append(f"JSON_FILES[{path!r}] = {json.dumps(payload, ensure_ascii=False, indent=2)!r}")
    lines.extend(
        [
            '',
            'def write_text(path: Path, content: str) -> None:',
            '    path.parent.mkdir(parents=True, exist_ok=True)',
            "    path.write_text(content, encoding='utf-8')",
            '',
            'def write_json(path: Path, content: str) -> None:',
            '    path.parent.mkdir(parents=True, exist_ok=True)',
            '    payload = json.loads(content)',
            "    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\\n', encoding='utf-8')",
            '',
            'def build_asset(asset_root: Path) -> None:',
            '    for relative_path, content in TEXT_FILES.items():',
            '        write_text(asset_root / relative_path, content)',
            '    for relative_path, content in JSON_FILES.items():',
            '        write_json(asset_root / relative_path, content)',
            '',
            'def main() -> None:',
            '    repo_root = Path(__file__).resolve().parents[2]',
            f"    build_asset(repo_root / 'assets' / {spec['id']!r})",
            f"    print(f\"Asset ready: {{repo_root / 'assets' / {spec['id']!r}}}\")",
            '',
            "if __name__ == '__main__':",
            '    main()',
        ]
    )
    return '\n'.join(lines) + '\n'


def build_verify_rules(spec: dict) -> str:
    trace_list = spec['accepted_sources'] + spec['rejected_sources'] + ['notes/triage_rules.md', 'README.txt', 'deliverables/README.md']
    protected_files = sorted(spec['asset_text'].keys()) + sorted(spec['asset_json'].keys())
    lines = [
        'from __future__ import annotations',
        '',
        'import argparse',
        'import json',
        'from pathlib import Path',
        '',
        f"TASK_ID = {spec['id']!r}",
        f"JSON_FILE = {spec['json_file']!r}",
        f"SUMMARY_FILE = {spec['summary_file']!r}",
        f"NOTE_FILE = {spec['note_file']!r}",
        f"EXPECTED_FIELDS = {repr(spec['expected_fields'])}",
        f"REQUIRED_ACCEPTED = set({repr(spec['accepted_sources'])})",
        f"REQUIRED_REJECTED = set({repr(spec['rejected_sources'])})",
        f"REQUIRED_TRACE = set({repr(trace_list)})",
        f"SUMMARY_KEYWORDS = {[item.lower() for item in spec['summary_keywords']]!r}",
        f"NOTE_KEYWORDS = {[item.lower() for item in spec['note_keywords']]!r}",
        f"FINAL_KEYWORDS = {[item.lower() for item in spec['final_keywords']]!r}",
        f"PROTECTED_FILES = {protected_files!r}",
        '',
        'def _read_text(path: Path) -> str:',
        "    return path.read_text(encoding='utf-8')",
        '',
        'def _read_json(path: Path):',
        "    return json.loads(path.read_text(encoding='utf-8'))",
        '',
        'def _check(condition: bool, weight: int, ok: str, fail: str) -> dict:',
        '    return {',
        "        'passed': bool(condition),",
        "        'weight': weight,",
        "        'earned': weight if condition else 0,",
        "        'reason': ok if condition else fail,",
        '    }',
        '',
        'def score_result(result_dir: Path):',
        "    workspace_after = result_dir / 'workspace_after'",
        "    workspace_before = result_dir / 'workspace_before'",
        "    deliverables = workspace_after / 'deliverables'",
        '    json_path = deliverables / JSON_FILE',
        '    summary_path = deliverables / SUMMARY_FILE',
        '    note_path = deliverables / NOTE_FILE',
        "    final_answer_path = result_dir / 'final_answer.md'",
        "    trace_path = result_dir / 'trace.jsonl'",
        '    checks = []',
        '',
        '    files_exist = all(path.exists() for path in [json_path, summary_path, note_path, final_answer_path, trace_path])',
        "    checks.append(_check(files_exist, 10, 'All required deliverables exist.', 'Missing required deliverables.'))",
        '',
        '    decision = _read_json(json_path) if json_path.exists() else {}',
        "    summary = _read_text(summary_path) if summary_path.exists() else ''",
        "    note = _read_text(note_path) if note_path.exists() else ''",
        "    final_answer = _read_text(final_answer_path) if final_answer_path.exists() else ''",
        "    trace = _read_text(trace_path) if trace_path.exists() else ''",
        '',
        '    field_match = isinstance(decision, dict) and all(decision.get(key) == value for key, value in EXPECTED_FIELDS.items())',
        "    source_audit_ok = isinstance(decision, dict) and REQUIRED_ACCEPTED.issubset(set(decision.get('accepted_sources', []))) and REQUIRED_REJECTED.issubset(set(decision.get('rejected_sources', [])))",
        "    checks.append(_check(field_match and source_audit_ok, 30, 'Decision payload and source audit are correct.', 'Decision payload or source audit is incomplete.'))",
        '',
        '    trace_ok = all(token in trace for token in REQUIRED_TRACE)',
        "    checks.append(_check(trace_ok, 20, 'Trace shows the expected no-skills audit path.', 'Trace indicates a shortcut path or missing evidence review.'))",
        '',
        '    summary_ok = all(keyword in summary.lower() for keyword in SUMMARY_KEYWORDS)',
        "    checks.append(_check(summary_ok, 15, 'Summary references the expected evidence and audit language.', 'Summary is missing required evidence discussion.'))",
        '',
        '    note_ok = all(keyword in note.lower() for keyword in NOTE_KEYWORDS)',
        "    checks.append(_check(note_ok, 10, 'Supporting note captures the expected operational details.', 'Supporting note misses the required operational details.'))",
        '',
        "    semantic_ok = all(keyword in (summary + '\\n' + final_answer).lower() for keyword in FINAL_KEYWORDS)",
        "    checks.append(_check(semantic_ok, 10, 'Semantic fallback check passed.', 'Semantic fallback check failed.'))",
        '',
        '    protected_ok = True',
        '    changed_files = []',
        '    if workspace_before.exists():',
        '        for relative_path in PROTECTED_FILES:',
        '            before_path = workspace_before / relative_path',
        '            after_path = workspace_after / relative_path',
        '            if before_path.exists() and after_path.exists() and _read_text(before_path) != _read_text(after_path):',
        '                protected_ok = False',
        '                changed_files.append(relative_path)',
        "    checks.append(_check(protected_ok, 5, 'Protected source files were left unchanged.', f'Protected source files changed: {changed_files}'))",
        '',
        '    score = sum(item[\'earned\'] for item in checks)',
        '    return {',
        "        'task_id': TASK_ID,",
        "        'result_dir': str(result_dir),",
        "        'score': score,",
        "        'passed': score >= 75,",
        "        'checks': checks,",
        '    }',
        '',
        'def main() -> None:',
        '    parser = argparse.ArgumentParser()',
        "    parser.add_argument('--result-dir', required=True)",
        "    parser.add_argument('--output', default=None)",
        '    args = parser.parse_args()',
        '',
        '    result_dir = Path(args.result_dir).expanduser().resolve()',
        '    payload = score_result(result_dir)',
        "    output = Path(args.output).expanduser().resolve() if args.output else result_dir / 'verify_result.json'",
        '    output.parent.mkdir(parents=True, exist_ok=True)',
        "    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\\n', encoding='utf-8')",
        '    print(json.dumps(payload, ensure_ascii=False, indent=2))',
        '',
        "if __name__ == '__main__':",
        '    main()',
    ]
    return '\n'.join(lines) + '\n'


def build_verify_prompt(spec: dict) -> str:
    return textwrap.dedent(f'''\
        You are grading the no-skills benchmark task {spec['id']} ({spec['name']}).

        Score out of 100. Combine:
        1. The structured output from `verify_rules.py`.
        2. `trace.jsonl` to confirm the agent actually inspected raw workspace evidence.
        3. `final_answer.md` and the deliverables written in `workspace_after/deliverables/`.

        Grading guidance:
        - Full credit requires the correct final conclusion plus evidence that the agent used current logs/config/data and explicitly rejected stale sources.
        - Deduct heavily if the final answer is correct but the trace suggests shortcutting, guessing, or skipping key evidence files.
        - Deduct for hallucinated facts, template contamination, unsupported claims, or failure to explain why stale evidence was rejected.
        - Deduct if deliverables are missing, badly structured, or contradict the structured verifier output.
        - Treat protected source file edits as a serious error.

        Return a concise score rationale that references both the structured checks and the observed trace behavior.
    ''').strip() + '\n'


def build_test_file() -> str:
    task_ids = [spec['id'] for spec in TASK_SPECS]
    task_ids_repr = json.dumps(task_ids)
    return textwrap.dedent(f'''\
        from __future__ import annotations

        import importlib.util
        import tempfile
        import unittest
        from pathlib import Path

        from nanoclaw.config import Settings
        from nanoclaw.task_loader import load_task_definition

        REPO_ROOT = Path(__file__).resolve().parents[1]
        TASK_IDS = {task_ids_repr}

        def _load_module(path: Path, module_name: str):
            spec = importlib.util.spec_from_file_location(module_name, path)
            if spec is None or spec.loader is None:
                raise RuntimeError(f"Cannot load module: {{path}}")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module

        class NoSkillsFamilySeedsChunkTest(unittest.TestCase):
            def test_task_yaml_loads_with_explicit_empty_skills(self) -> None:
                settings = Settings.from_env()
                for task_id in TASK_IDS:
                    task_path = REPO_ROOT / 'tasks' / f'{{task_id}}.yaml'
                    task = load_task_definition(task_path, settings)
                    self.assertEqual(task.task_id, task_id)
                    self.assertTrue(task.skills.available_explicit)
                    self.assertEqual(task.skills.available, ())

            def test_prompts_stay_natural(self) -> None:
                for task_id in TASK_IDS:
                    prompt = (REPO_ROOT / 'tasks' / 'prompts' / f'{{task_id}}.md').read_text(encoding='utf-8')
                    self.assertNotIn('accepted_sources', prompt)
                    self.assertNotIn('rejected_sources', prompt)
                    self.assertNotIn('accepted source', prompt.lower())
                    self.assertNotIn('rejected source', prompt.lower())
                    self.assertIn('deliverables', prompt)

            def test_env_builders_and_verifiers_import(self) -> None:
                with tempfile.TemporaryDirectory() as tmpdir:
                    tmp_root = Path(tmpdir)
                    for task_id in TASK_IDS:
                        env_builder = _load_module(REPO_ROOT / 'tasks' / task_id / 'env_builder.py', f'env_{{task_id}}')
                        verifier = _load_module(REPO_ROOT / 'tasks' / task_id / 'verify_rules.py', f'verify_{{task_id}}')
                        asset_root = tmp_root / 'assets' / task_id
                        env_builder.build_asset(asset_root)
                        self.assertTrue((asset_root / 'README.txt').exists())
                        self.assertTrue((asset_root / 'deliverables' / 'README.md').exists())
                        self.assertTrue((asset_root / 'notes' / 'triage_rules.md').exists())
                        self.assertTrue(hasattr(verifier, 'score_result'))

        if __name__ == '__main__':
            unittest.main()
    ''')


def main() -> None:
    for spec in TASK_SPECS:
        task_id = spec['id']
        write_text(REPO_ROOT / 'tasks' / f'{task_id}.yaml', build_yaml(spec))
        write_text(REPO_ROOT / 'tasks' / 'prompts' / f'{task_id}.md', spec['prompt'])
        write_text(REPO_ROOT / 'tasks' / task_id / 'env_builder.py', build_env_builder(spec))
        write_text(REPO_ROOT / 'tasks' / task_id / 'verify_rules.py', build_verify_rules(spec))
        write_text(REPO_ROOT / 'tasks' / task_id / 'verify_prompt.md', build_verify_prompt(spec))
        write_text(REPO_ROOT / 'tasks' / task_id / 'report.md', spec['report_text'])
    write_text(REPO_ROOT / 'tests' / 'test_no_skills_family_seeds_chunk54_60.py', build_test_file())

if __name__ == '__main__':
    main()
