# Configuration

## Summary

Configure deterministic, investigation, and optional AI explanation modes.

## Prerequisites

- DEDoc installed
- Basic familiarity with `dedoc diagnose`

## Steps

### Deterministic mode (default)

No AI configuration required:

```bash
dedoc diagnose error.log
```

### Investigation mode (optional)

```bash
dedoc diagnose error.log --investigate --context context.yaml
```

### AI explanation mode (optional)

```bash
export DEDOC_AI_PROVIDER=ollama
export DEDOC_AI_MODEL=llama3.2
dedoc diagnose error.log --ai
```

## Flags and environment variables

| Scope | Option / Variable | Purpose |
| --- | --- | --- |
| Output | `--format` | `text`, `json`, `markdown` |
| Input parsing | `--input-format` | `auto`, `text`, `json`, `jsonl` |
| Definitions | `--diagnoses-path` | Override diagnosis directory |
| Investigation | `--investigate`, `--context` | Enable structured context probing |
| AI toggle | `--ai` | Enable AI explanation mode |
| AI provider | `--provider` / `DEDOC_AI_PROVIDER` | Provider selection |
| AI model | `--ai-model` / `DEDOC_AI_MODEL` | Model or deployment |
| AI endpoint | `--ai-base-url` / `DEDOC_AI_BASE_URL` | Custom provider endpoint |
| OpenAI key | `DEDOC_OPENAI_API_KEY` | Required for `openai` |
| Azure key | `DEDOC_AZURE_OPENAI_API_KEY` | Required for `azure_openai` |
| Azure endpoint | `DEDOC_AZURE_OPENAI_ENDPOINT` | Required for `azure_openai` |
| Anthropic key | `DEDOC_ANTHROPIC_API_KEY` | Required for `anthropic` |

## Expected output

- Deterministic report always available without AI keys
- AI explanation appended only when provider is available and `--ai` is set

## Common errors

| Problem | Likely cause | Fix |
| --- | --- | --- |
| AI section missing | `--ai` not set or provider unavailable | Set `--ai` and valid provider config |
| Provider config error | Missing env vars | Export required key/endpoint |
| Investigation skipped | Missing context file | Pass valid `--context` path |

!!! tip "See also"
    - [CLI reference](../reference/cli.md)
    - [Security model](../explanation/security-model.md)
    - [Troubleshooting](troubleshooting.md)
