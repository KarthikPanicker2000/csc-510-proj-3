# Prompt Notes: Model Evaluation on MealSlot (qwen3:8b, local)

## Executive Summary & Model Configuration

The evaluation report indicates that prompts requiring static analysis of the repo
were answered, such as the onboarding checklist found in the output. However, prompts
needing git history, a running build, or credentials remained unanswered. The single
most important finding is the presence of large files in critical components, which
may impact performance and maintainability.

**Configuration.** qwen3:8b served locally through Ollama, thinking disabled, context
window 24,576 tokens, temperature 0.25. Source was supplied with line numbers
prepended so citations could be checked. 9 of 15 prompts were run (not run: 2, 3, 6,
7, 9, 10).

**Citation audit.** 3 of 3 citations resolved to a real file and a line within that
file. 0 did not, and are marked ⚠️UNVERIFIED inline. Treat unverified citations as
claims, not evidence.

---

## 1. Prompt Performance & Evaluation Notes

| Prompt # & Goal | Status | Key Findings & Evaluation |
|---|---|---|
| **1: First contact with repo** | Abandoned | Evaluation pass failed to parse. |
| **4: Undocumented product features** | Abandoned | Evaluation pass failed to parse. |
| **5: Rotten / fragile areas** | Earned Keep | `llm.ts:287` (large file size), `route.ts:214` (large file size), `PartySpinMachine.tsx:385` (large file size) |
| **8: Two-way traceability** | Abandoned | Evaluation pass failed to parse. |
| **11: The dependency map** | Abandoned | Evaluation pass failed to parse. |
| **12: The public surface** | Abandoned | Evaluation pass failed to parse. |
| **13: Naming and pattern drift** | Abandoned | Structured evaluation was salvaged from malformed output; findings may be incomplete. |
| **14: The data model, reconstructed** | Abandoned | Evaluation pass failed to parse. |
| **15: Onboarding from the outside** | Earned Keep | The output provides a detailed setup checklist for the MealSlot project, including steps for cloning the repository, installing dependencies, setting up the database, and configuring environment variables. It also outlines optional setups for Docker, CI/CD, and various testing frameworks. |

Prompts 2, 3, 6, 7, 9, and 10 were not run.

---

## 2. Caught Issues

No defects with supporting citations were produced.

---

## 3. Strengths & Weaknesses of qwen3:8b on This Task

### Strengths

None recorded.

### Weaknesses

None recorded.

---

*Independent verification of this run's one falsifiable claim (the three Prompt 5
citations) against the live repo is in
[Model_Verdict_Comparison.md](Model_Verdict_Comparison.md#4-a-fourth-data-point-qwen38b-local-non-comparable)
— all three resolved exactly. That comparison also covers why this run isn't scored
against the Gemini/Sonnet 5/GPT-5.6 Sol reports on the same axis.*
