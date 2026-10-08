## Summary

<!-- One or two sentences. What does this change and why? -->

## Type of change

- [ ] Bug fix
- [ ] New diagnosis
- [ ] Fixtures / test coverage
- [ ] Documentation
- [ ] CI / release tooling
- [ ] Dependency update

## Checklist

- [ ] `make verify` passes locally
- [ ] If I added a diagnosis: it has a positive fixture with the expected ID(s)
      and `confidence_band`, plus a negative guard
- [ ] If I added a signal: no invented error semantics; the signature is
      validated or labelled as an unverified hypothesis
- [ ] If I added a reference URL: it is reachable (the link-check runs in
      `make verify`)
- [ ] Changelog updated (if user-facing)
- [ ] Docs updated (if user-facing)

## Related issues

<!-- Closes #NNN or links to a diagnosis request -->