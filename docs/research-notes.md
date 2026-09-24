# Research and artifact map

The source material in `../NeurIPS_2026_clawbench` describes ClawBenchPro as a
workspace-grounded benchmark for autonomous agents. The released package in
`data/ClawBenchPro` is the executable artifact: task YAML defines runtime
configuration, prompts define the user interaction, builders create an isolated
workspace, and verifiers inspect the final workspace state.

The package has two public subsets:

| subset | tasks | groups |
| --- | ---: | --- |
| `round_01_aligned_mix_800` | 800 | base, hard_aligned, multi_turn_aligned, skills_aligned |
| `persona_aligned_mix_200` | 200 | base, hard, multi_turn, skills |

The paper discusses 43 professional domains and comparisons among four
harnesses. Re-running those comparisons requires model API access and, for the
Docker adapters, local images and credentials accepted by the selected harness.
Results are intentionally not committed to this repository.

