# CSC 510 Project 1a Deliverables

This directory separates coursework artifacts from the cloned MealSlot product in `proj2/mealslot`.

## Structure

```text
deliverables/
├── members/                 # Individual model runs and contributions
│   ├── karthik/
│   ├── cameron/
│   ├── carlos/
│   └── sebastian/
├── final/                   # Reconciled team deliverables used in the report
│   ├── D1-product-choice/
│   ├── D2-use-cases/
│   ├── D3-tests-and-results/
│   ├── D4-traceability/
│   ├── D5-prompt-notes/
│   ├── report/
│   └── demo/
└── templates/               # Shared tables for consistent reporting
```

## Rules

1. Each member commits their own source artifacts under `members/<name>/` using their own GitHub account.
2. Do not overwrite another member's artifacts. Reconciliation happens through pull requests into `final/`.
3. Keep meaningful commits small and steady; do not submit all work in one final commit.
4. Do not commit `.env`, `.env.local`, passwords, API keys, tokens, private account data, or database dumps.
5. Do not commit `node_modules`, complete Playwright report directories, or every generated trace/video.
6. Commit small raw-output text samples and selected failure screenshots. Store large videos/traces externally and link them from the relevant Markdown file.
7. Automated test code belongs in `proj2/mealslot/tests/`; D3 contains links to that code plus curated output and the results table.
8. Project 1a reports product behavior as-is. Do not change MealSlot product code merely to make a new test pass.

## Recommended workflow

```powershell
git pull origin main
git checkout -b <name>/<short-task>
git add deliverables/<path> proj2/mealslot/tests/<path>
git commit -m "docs: add <member> use-case analysis"
git push -u origin <name>/<short-task>
```

Open a pull request, have another member review it, and merge it into the team's working branch.

## Naming convention

Use descriptive names that identify the deliverable, contributor/model, and artifact type:

```text
D2_Karthik_Codex_use_cases.md
D2_Cameron_Gemini_use_cases.md
D3_Carlos_test_design.md
D3_Sebastian_raw_output.txt
D5_Karthik_Codex_prompt_notes.md
```

