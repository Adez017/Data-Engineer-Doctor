# AGENTS.md

## Push policy (MANDATORY)

- Never `git push` (commits, branches, or tags) without explicit user permission in the current session.
- Before any push, provide a concise summary of the changes: what commits/files/tags are involved, the target branch, and the reason for the push.
- Wait for the user to explicitly approve before running the push command.
- Maintain the existing annotated tag `v0.1.0`; never recreate it.