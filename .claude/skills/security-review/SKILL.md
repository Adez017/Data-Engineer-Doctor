---
name: security-review
description: This skill should be used when reviewing DEDoc changes for privacy and security, especially input parsing, provider/AI networking, redaction, path handling, and dependencies. Trigger phrases include "security review", "privacy review", "redaction check", "is this safe".
version: 0.1.0
---

# Security and privacy review

DEDoc reads untrusted failure logs and can optionally call an AI provider, so
privacy is a core property (BUILD_PLAN.md §14). Run this review for any change
in those areas.

## Checklist

1. **No secrets persisted or logged.** Grep the diff for tokens, passwords,
   `Authorization`, connection strings, and full signed URLs. Provider calls
   must redact before egress (`dedoc/providers`).
2. **Network egress is intentional.** Only the provider layer and
   `make link-check` make outbound calls. No new egress paths.
3. **Untrusted input is data, not code.** No `eval`/`exec`/`subprocess` built
   from log content; no unvalidated paths from fixtures/logs.
4. **Prompt-injection resistance.** Agent/tool prompts treat log text as
   data; instructions inside logs must not change agent behavior.
5. **Supply chain.** `make audit` (pip-audit) passes; new deps are justified
   and pinned sensibly.
6. **CI credentials.** Publishing uses OIDC (`id-token: write`); no long-lived
   secrets committed or printed.

## Commands

```bash
make audit
git diff --staged            # inspect the actual surface
```

## Output

Report each finding as `file_path:line`, severity (high/medium/low), the risk,
and a minimal fix. If clean, state that explicitly and list what you checked.
Do not rewrite code or push; escalate findings to the change author.
