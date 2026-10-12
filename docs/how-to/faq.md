# FAQ

## Summary

Answers to frequent user questions about behavior, safety, and usage patterns.

## Prerequisites

- None

## Questions and answers

### Does DEDoc require AI or API keys?
No. Deterministic mode is default and requires no keys.

### When does data leave my machine?
Only when AI explanation mode is explicitly enabled.

### Why did I get `insufficient_evidence`?
The top candidate did not meet minimum score threshold.

### Can I use DEDoc in CI?
Yes, use JSON output and publish results as artifacts.

### Can I override diagnosis definitions?
Yes, with `--diagnoses-path`.

### Does investigation mode mutate systems?
No. Investigation probes are read-only and bounded.

### What inputs are supported?
Text logs, JSON events, JSON arrays, JSONL/NDJSON.

### How do I force input parsing mode?
Use `--input-format`.

### Can I use local models?
Yes, e.g. provider `ollama`.

### Is output schema stable?
Core fields are versioned; see compatibility page.

!!! tip "See also"
    - [When to use DEDoc](when-to-use.md)
    - [Top 25 user queries map](../reference/top-25-queries.md)
    - [Versioning & compatibility](../explanation/versioning-compatibility.md)
