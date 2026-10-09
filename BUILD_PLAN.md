DATA ENGINEER DOCTOR

Open-source, evidence-driven diagnosis for modern data engineering failures

MASTER BUILD & IMPLEMENTATION PLAN

```
North Star: Turn messy data-engineering failures into evidence-backed, actionable diagnoses, without turning the product into a generic AI wrapper.
```

Document purpose: This document is the implementation source of truth for Claude Code and human contributors. It defines product scope, architecture, AI/agentic behavior, validation, security, testing, contribution workflow, milestones, and release criteria.

Initial target: PySpark / Apache Spark / Databricks engineers, with a vendor-neutral architecture that can expand to ADF, Microsoft Fabric, Airflow, dbt, Snowflake, BigQuery, AWS Glue, and other systems.

# 1. Product Definition

Data Engineer Doctor (DEDoc) is an open-source diagnostic engine for data-engineering failures. It accepts logs, error messages, structured events, and optional runtime context; normalizes them; applies deterministic diagnostic rules; optionally performs agentic investigation through controlled tools; ranks hypotheses using evidence; and produces an actionable report.

## Core promise

```
Input
  logs + error + metadata + optional historical context
        ↓
Normalization
        ↓
Deterministic diagnosis engine
        ↓
Evidence extraction
        ↓
Agentic investigation (optional)
        ↓
Hypothesis ranking + verification
        ↓
Fix + prevention recommendations
        ↓
Human-readable / JSON / Markdown report
```

## What this is NOT

- Not a chatbot that simply forwards an error to an LLM.

- Not a production auto-remediation system in the initial releases.

- Not an Azure-only product.

- Not a replacement for observability platforms.

- Not a system that claims certainty when evidence is insufficient.

# 2. Problem Statement

Data engineers spend substantial time triaging failures across Spark, Databricks, orchestration systems, storage, SQL engines, schemas, and data-quality checks. Logs are often noisy, the true root cause can occur earlier than the final exception, and the same failure patterns repeatedly require manual investigation.

The product should reduce time-to-diagnosis by converting raw failure evidence into a structured investigation and a defensible explanation.

## Primary user questions

- What actually failed?

- What is the most likely root cause?

- What evidence supports that conclusion?

- What alternative causes were considered?

- What should I do now?

- How do I prevent the failure from recurring?

# 3. Product Principles

| Principle | Requirement |
| --- | --- |
| Evidence over intuition | Every diagnosis should point to observable signals, rules, or source evidence. |
| Deterministic core | The core engine must remain useful with AI disabled. |
| AI as investigator | AI should gather, correlate, compare, and explain evidence rather than inventing facts. |
| Uncertainty is a valid answer | The system must explicitly return insufficient evidence when appropriate. |
| Vendor neutral | Platform adapters live at the edge; the diagnostic model remains portable. |
| Privacy by default | Local parsing/redaction and optional AI providers; no mandatory cloud upload. |
| Contributor friendly | Adding a diagnosis should be possible without understanding the entire codebase. |
| Reproducible | Known failures must have fixtures and regression tests. |
| No unsafe automation | Initial releases never mutate production resources. |

# 4. MVP Scope

| Area | MVP v0.1 |
| --- | --- |
| Input | TXT, JSON, JSONL, direct CLI error text |
| Platforms | Apache Spark, PySpark, Databricks-style failures |
| Diagnoses | 30 high-value failure patterns |
| Engine | Deterministic rules + evidence scoring |
| AI | Optional; disabled by default |
| Agentic workflow | Optional investigation for structured context |
| Output | CLI, JSON, Markdown |
| Safety | No automatic production changes |
| Packaging | Python package + CLI |
| Distribution | PyPI + GitHub |

## Non-goals for v0.1

- No full web application.

- No mandatory cloud account.

- No automatic cluster/pipeline modifications.

- No broad support for every data platform.

- No autonomous agent with unrestricted shell or production access.

- No claims of root-cause certainty without supporting evidence.

# 5. First Diagnostic Knowledge Base

| Category | Initial patterns |
| --- | --- |
| Schema | Type mismatch; missing column; unexpected column; duplicate column; schema evolution failure; nested schema mismatch |
| Data quality | Null violation; duplicates; invalid date; invalid numeric value; referential integrity issue |
| Spark | Executor OOM; driver OOM; executor lost; repeated task failure; data skew; shuffle fetch failure; broadcast timeout; stage failure |
| Delta | Concurrent modification; schema mismatch; table not found; invalid partition; transaction conflict |
| Connectivity | Authentication failure; connection timeout; DNS failure; permission denied; endpoint unavailable |
| Performance | Small files; excessive shuffle; missing partition pruning; oversized broadcast |

Each diagnosis receives a stable ID, for example DEDOC-SPARK-006. IDs become part of the public API and should not be casually renamed.

# 6. Diagnosis Specification

Diagnostic knowledge must be machine-readable and independently testable.

```
id: DEDOC-SPARK-006
name: Shuffle Fetch Failure
category: spark.shuffle

severity:
  default: high

platforms:
  - spark
  - databricks

patterns:
  exception_types:
    - FetchFailedException

signals:
  positive:
    - executor_lost
    - shuffle_file_missing
    - repeated_stage_failure
  negative:
    - dns_failure
    - authentication_failure

hypotheses:
  - executor_loss
  - shuffle_corruption
  - network_failure

recommendations:
  immediate: []
  recommended: []
  prevention: []

references:
  - source: official documentation
    url: <validated URL>

tests:
  fixtures:
    - fixture-name
```

# 7. System Architecture

```
DATA ENGINEER DOCTOR
                                  │
                           Failure Intake
                                  │
                           Normalization
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
             Deterministic Engine        Context Adapters
                    │                           │
                    └─────────────┬─────────────┘
                                  │
                           Evidence Store
                                  │
                           Agent Orchestrator
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
        Intake Agent       Investigation Agent   Knowledge Agent
              │                   │                   │
              └───────────────────┼───────────────────┘
                                  │
                          Diagnosis / Ranking
                                  │
                         Verification Agent
                                  │
                        Remediation Agent
                                  │
                            Final Report
```

## Architectural boundary

The deterministic engine, schemas, diagnosis knowledge, parsers, and evaluation framework must remain independently usable. AI is an optional reasoning layer around these components.

# 8. Canonical Failure Model

Use OpenTelemetry concepts where they fit rather than inventing incompatible telemetry semantics. Preserve raw vendor-specific attributes separately.

```
FailureEvent
- id
- timestamp
- platform
- service
- job
- stage
- task
- severity
- error_type
- error_message
- stacktrace
- source
- resource_attributes
- event_attributes
- raw_payload
```

The implementation should map common concepts such as error type, exception information, timestamp, resource, and attributes to the canonical model, while retaining vendor-specific details.

# 9. Diagnostic Pipeline

1. Parse and normalize the input.

2. Detect platform and execution engine.

3. Extract structured signals from error text, stack traces, metadata, and timestamps.

4. Match deterministic diagnosis rules.

5. Generate initial hypotheses.

6. If enabled and context is available, invoke the investigation agent.

7. Collect and graph evidence.

8. Rank hypotheses using explicit scoring.

9. Run verification checks.

10. Generate remediation and prevention recommendations.

11. Render the final report.

12. Record evaluation telemetry without leaking secrets or sensitive payloads.

# 10. Evidence & Confidence Model

Confidence must be derived from evidence, not from the LLM's self-reported certainty.

| Signal | Example weight |
| --- | --- |
| Exact known error signature | 40 |
| Platform/engine match | 20 |
| Stack-trace evidence | 20 |
| Correlated runtime signal | 15 |
| Supporting metadata | 5 |

These values are an initial implementation hypothesis, not a scientific truth. They must be calibrated against an evaluation dataset and versioned when changed.

Recommended output bands: HIGH, MEDIUM, LOW. Always expose the evidence and competing hypotheses when material.

# 11. Agentic AI Architecture

Agentic AI is used only where iterative investigation adds value.

| Agent | Responsibilities | Restrictions |
| --- | --- | --- |
| Intake Agent | Classify platform, normalize context, identify missing evidence | Cannot claim root cause |
| Investigation Agent | Choose tools, inspect logs/metrics/schema/history, test hypotheses | Tool allowlist; bounded calls/iterations |
| Knowledge Agent | Retrieve relevant diagnosis patterns and references | Read-only |
| Diagnosis Agent | Compare hypotheses and produce evidence-backed ranking | Must cite evidence |
| Verification Agent | Challenge diagnosis, seek contradictory evidence | Independent reasoning path |
| Remediation Agent | Produce fixes and prevention steps | Suggestion only in MVP |

## Agent loop

```
Observe
  ↓
Hypothesize
  ↓
Select approved tool
  ↓
Collect evidence
  ↓
Update hypotheses
  ↓
Check contradiction / missing evidence
  ↓
Verify
  ↓
Stop
```

Hard limits must be configurable. Initial defaults: maximum 8 investigation iterations, maximum 20 tool calls, and a bounded execution timeout. The agent must stop when evidence is sufficient or when limits are reached.

# 12. Tool & MCP Architecture

Expose controlled investigation capabilities as tools. MCP may be used as the interoperability layer for external systems, but the core package must not depend on MCP to perform local diagnosis.

```
doctor.tools
├── get_logs
├── search_logs
├── get_pipeline_run
├── get_previous_runs
├── compare_runs
├── get_schema
├── compare_schema
├── get_metrics
├── get_stage_metrics
├── get_executor_metrics
├── inspect_query_plan
└── search_knowledge_base
```

Every tool must declare input schema, output schema, read/write behavior, security classification, timeout, and whether it is permitted in local/CI/cloud execution.

# 13. AI Provider Abstraction

| Provider | MVP status |
| --- | --- |
| No AI / deterministic | Required |
| Local model / Ollama-compatible | Optional |
| OpenAI-compatible endpoint | Optional |
| Anthropic | Optional |
| Azure OpenAI | Optional |

Provider-specific SDKs must be isolated behind an interface. The core diagnostic engine must never require a provider API key.

# 14. Privacy & Security

- Default to local parsing and deterministic analysis.

- Implement secret and credential redaction before external AI calls.

- Detect common connection strings, tokens, API keys, passwords, authorization headers, and sensitive identifiers.

- Never execute arbitrary commands from an LLM recommendation.

- Never allow an agent to mutate production resources in MVP.

- Use explicit tool allowlists.

- Treat log content as untrusted input and defend against prompt injection.

- Never expose raw logs in telemetry or analytics by default.

- Document exactly what leaves the local environment when optional AI is enabled.

- Pin and audit dependencies; run dependency and static security checks in CI.

# 15. Repository Structure

```
data-engineer-doctor/
├── dedoc/
│   ├── cli/
│   ├── core/
│   ├── models/
│   ├── parser/
│   ├── analyzer/
│   ├── diagnosis/
│   ├── evidence/
│   ├── agents/
│   ├── tools/
│   ├── providers/
│   ├── formatters/
│   └── integrations/
├── diagnoses/
│   ├── spark/
│   ├── databricks/
│   ├── schema/
│   ├── quality/
│   ├── delta/
│   ├── connectivity/
│   └── performance/
├── fixtures/
│   ├── real/
│   ├── synthetic/
│   └── negative/
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── regression/
│   └── evals/
├── docs/
├── examples/
├── benchmarks/
├── .claude/
│   ├── agents/
│   ├── skills/
│   └── settings.json
├── .github/
│   ├── workflows/
│   ├── ISSUE_TEMPLATE/
│   └── pull_request_template.md
├── pyproject.toml
├── Makefile
├── README.md
├── CONTRIBUTING.md
├── SECURITY.md
├── CODE_OF_CONDUCT.md
├── LICENSE
└── BUILD_PLAN.md
```

# 16. Recommended Technology Stack

| Component | Choice |
| --- | --- |
| Language | Python 3.11+ |
| CLI | Typer |
| Data models | Pydantic |
| Configuration / diagnosis | YAML |
| Testing | Pytest |
| Linting / formatting | Ruff |
| Type checking | mypy or pyright |
| Documentation | MkDocs |
| CI/CD | GitHub Actions |
| Packaging | pyproject.toml + PyPI |
| API later | FastAPI |
| Agent interoperability | MCP-compatible tooling where useful |
| License | Apache-2.0 |

# 17. Claude Code Development System

Claude Code should be treated as a coordinated engineering team, not a single autonomous coder.

```
.claude/
├── agents/
│   ├── architect.md
│   ├── backend-engineer.md
│   ├── diagnosis-engineer.md
│   ├── ai-agent-engineer.md
│   ├── test-engineer.md
│   ├── security-reviewer.md
│   ├── documentation-engineer.md
│   └── oss-maintainer.md
├── skills/
│   ├── add-diagnosis/
│   ├── add-platform/
│   ├── run-evals/
│   ├── security-review/
│   └── release/
└── settings.json
```

## Claude Code operating rules

- BUILD_PLAN.md is the source of truth.

- Do not implement future phases unless explicitly requested.

- Before editing, inspect the relevant code and existing tests.

- Prefer small vertical slices over large speculative rewrites.

- Never declare completion without running the required verification command.

- If requirements are ambiguous, document the ambiguity and stop rather than inventing behavior.

- Any new diagnosis must include positive, negative, and regression fixtures.

- Any AI behavior must have deterministic evaluation cases.

- Any security-sensitive change requires the security-reviewer agent.

- Any public API change requires documentation and compatibility review.

# 18. Verification Command

Create one authoritative local command. CI and Claude Code must use the same verification pipeline.

```
make verify
```

It should execute, as applicable:

- Formatting check

- Lint

- Type checking

- Unit tests

- Integration tests

- Diagnosis schema validation

- Fixture validation

- Regression tests

- Agent evaluations

- Security checks

- Documentation/link checks

- Package build

```
Definition of done: A feature is not complete until make verify passes, documentation is updated, and the relevant acceptance criteria are satisfied.
```

# 19. Evaluation Framework

Evaluation is a first-class product component, not a later optimization.

| Metric | Meaning |
| --- | --- |
| Diagnosis accuracy | Correct diagnosis among known cases |
| Precision | How often a diagnosis is correct when returned |
| Recall | How many known applicable cases are detected |
| Evidence coverage | Percentage of conclusions supported by explicit evidence |
| Tool efficiency | Useful evidence obtained per tool call |
| Unsupported-claim rate | Conclusions not justified by available evidence |
| Abstention quality | Ability to say insufficient evidence when appropriate |
| Remediation validity | Whether suggested fixes are technically appropriate |
| Regression rate | Previously correct cases that become incorrect |

Create a benchmark corpus containing real-world-style, synthetic, and adversarial failures. Do not use private customer logs without explicit permission and sanitization.

# 20. Testing Strategy

| Layer | Purpose |
| --- | --- |
| Unit | Models, parsers, rules, scoring |
| Integration | End-to-end diagnosis pipeline |
| Regression | Known failures remain stable |
| Negative | Avoid false positives |
| Security | Prompt injection, secret leakage, unsafe tool use |
| Agent eval | Tool selection, reasoning, evidence use, abstention |
| Performance | Large logs, many events, bounded runtime |
| Compatibility | Supported Python/platform versions |

# 21. Implementation Phases

| Phase | Work | Exit criterion |
| --- | --- | --- |
| Phase 0 - Specification | Finalize architecture, contracts, coding rules, evaluation format. | Approved architecture + repository plan. |
| Phase 1 - Foundation | Package, CLI, models, diagnosis schema, rule engine, CI. | A simple error can be parsed and diagnosed. |
| Phase 2 - 30 Diagnoses | Build Spark/Databricks knowledge base and fixtures. | 30 diagnoses pass positive/negative/regression tests. |
| Phase 3 - Evidence Engine | Evidence extraction, scoring, competing hypotheses. | Reports explain why a diagnosis was selected. |
| Phase 4 - Agentic Investigation | Tool interface, investigation agent, verification agent. | Agent can investigate structured context with bounded calls. |
| Phase 5 - AI Provider Layer | Provider abstraction, redaction, optional AI explanation. | AI is optional and privacy behavior is tested. |
| Phase 6 - Developer Integrations | GitHub Action, JSON/Markdown outputs, SDK. | Doctor can run in CI. |
| Phase 7 - Platform Expansion | ADF, Fabric, Airflow/dbt or next validated demand. | At least one additional platform adapter. |
| Phase 8 - Public Launch | Docs, demo, contribution campaign, release. | First public stable release. |

# 22. Milestone Acceptance Criteria

| ID | Milestone | Acceptance criteria |
| --- | --- | --- |
| M1 | CLI works locally | Install succeeds; diagnose command works; JSON output valid. |
| M2 | 30 diagnosis MVP | Every diagnosis has fixtures, tests, docs, and references where available. |
| M3 | Evidence-based reports | Every high/medium-confidence conclusion exposes supporting evidence. |
| M4 | Safe agentic investigation | Agent uses only approved tools and respects iteration/call/time limits. |
| M5 | AI optionality | System works fully with AI disabled; provider integration is isolated. |
| M6 | Security baseline | Secrets are redacted; unsafe actions blocked; security tests pass. |
| M7 | OSS readiness | Contribution guide, issue templates, code of conduct, license, docs, CI. |

# 23. Open-Source Contribution Model

The contribution model should make small, meaningful PRs possible.

- Add one diagnosis.

- Add one platform error pattern.

- Add one negative fixture.

- Improve evidence extraction.

- Add a parser.

- Add documentation.

- Add an evaluation case.

- Improve CLI output.

- Add a tool adapter.

- Improve redaction/security.

Every diagnosis issue should contain: error pattern, expected diagnosis, example input, expected output, relevant official reference, test requirements, and documentation requirements.

# 24. Public Launch Strategy

The initial audience should be PySpark, Databricks, Spark, Azure Data Engineering, and adjacent data-engineering communities.

1. Release the MVP with a short demo showing a real failure going from raw log to evidence-backed diagnosis.

2. Publish individual diagnosis patterns as technical content rather than generic product promotion.

3. Ask the community which failures waste the most time and convert validated responses into issues.

4. Run a contributor campaign focused on adding diagnosis patterns and fixtures.

5. Publish benchmark results so the project can be evaluated on engineering merit.

North-star community metric: failures successfully diagnosed. Secondary metrics: active contributors, diagnosis patterns, supported platforms, evaluations, and successful installations.

# 25. Future Roadmap

```
v0.1
Spark + Databricks
30 diagnoses
CLI
Deterministic engine
Evidence scoring

v0.2
OpenTelemetry normalization
ADF
Fabric
GitHub Action
AI explanation

v0.3
MCP/tool ecosystem
Agentic investigation
Historical comparisons
Schema/query-plan tools

v1.0
Python SDK
REST API
Web playground
Multiple platform adapters
Large evaluation corpus

Future
Observability integrations
Team analytics
Historical failure intelligence
Optional hosted service
Enterprise integrations
Community-maintained diagnostic knowledge base
```

# 26. First Build Sprint

Claude Code should execute the following sequence and stop after each acceptance gate.

1. Create repository structure and pyproject.toml.

2. Implement canonical FailureEvent model.

3. Implement Diagnosis model and YAML loader.

4. Implement one end-to-end rule: Spark schema mismatch.

5. Implement CLI: dedoc diagnose <file>.

6. Add positive, negative, and malformed fixtures.

7. Implement JSON and Markdown output.

8. Create make verify.

9. Add CI workflow running make verify.

10. Only after the deterministic path is green, add evidence scoring.

11. Only after evidence scoring is green, implement the first bounded investigation-agent prototype.

```
Do not begin with the agent. Prove that the deterministic diagnostic path works first. Then use AI to investigate gaps that deterministic rules cannot efficiently resolve.
```

# 27. Definition of Done for the Entire Project

- A user can install the package with a documented command.

- A user can diagnose a supported failure locally without an AI API key.

- Every published diagnosis has reproducible fixtures and regression tests.

- The system exposes evidence supporting its conclusions.

- The system can abstain when evidence is insufficient.

- AI is optional and provider-independent.

- Agentic workflows have bounded tools, iterations, timeouts, and security controls.

- Sensitive log content is protected by default.

- CI validates formatting, types, tests, security, package build, and evaluations.

- Contributors can add a diagnosis without modifying core engine code.

- Documentation is sufficient for an external contributor to make a first PR.

- Benchmark results are published with the release.

- No feature is described as production-ready until its acceptance criteria and evaluation evidence support that claim.

# 28. Claude Code Master Instruction

Place the following instruction in the repository's Claude Code operating guidance or use it as the initial project instruction.

```
You are working on Data Engineer Doctor (DEDoc), an open-source,
evidence-driven diagnostic engine for data engineering failures.

BUILD_PLAN.md is the source of truth.

Rules:
1. Work only within the current phase unless explicitly asked to advance.
2. Inspect existing code, tests, and documentation before editing.
3. Prefer small vertical slices that produce a working, tested capability.
4. Never invent external facts, APIs, error semantics, or documentation links.
5. Validate vendor-specific behavior against authoritative documentation
   or clearly label it as an unverified hypothesis.
6. The deterministic engine must remain useful without AI.
7. AI must investigate and explain evidence; it must not be treated as
   an unquestionable source of truth.
8. Every diagnosis requires positive, negative, and regression fixtures.
9. Every agentic feature requires bounded tools, bounded iterations,
   explicit schemas, security controls, and evaluation cases.
10. Never expose secrets or raw sensitive logs to external AI providers.
11. Never perform production mutations in the MVP.
12. Do not declare a task complete until make verify passes.
13. If a requirement is ambiguous, stop and document the ambiguity rather
   than silently inventing behavior.
14. Update documentation and tests with every behavior change.
15. Preserve backward compatibility for public diagnosis IDs and CLI behavior.
16. When changing an architectural contract, update BUILD_PLAN.md or create
   a documented architecture decision record before implementation.

Completion report must include:
- What changed
- Files changed
- Tests executed
- Evaluation results
- Security considerations
- Known limitations
- Whether make verify passed
```

# 29. Recommended First Repository Files

```
BUILD_PLAN.md
README.md
CONTRIBUTING.md
CODE_OF_CONDUCT.md
SECURITY.md
LICENSE
pyproject.toml
Makefile

dedoc/
tests/
diagnoses/
fixtures/
docs/

.claude/
.github/
```

# 30. Final Product Direction

```
The long-term moat is not the LLM. The moat is the community-maintained, testable diagnostic knowledge + evidence graph + platform integrations + evaluation corpus.
```

The project should become a shared reliability layer for data engineers: a tool that understands recurring failure patterns, investigates them with controlled agents, explains conclusions with evidence, and continuously improves through community contributions.

The correct first move is therefore not to build a flashy AI agent. Build a trustworthy diagnostic kernel, prove it with real and synthetic failure cases, then add agentic investigation where it measurably improves diagnosis quality.
