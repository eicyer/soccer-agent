# Secrets never share a job with repository code

In GitHub Actions, a job that runs our Python code, its dependencies or third-party build actions gets no secrets. Work that needs a secret runs in a separate job that receives the earlier job's output as an artifact, runs only fixed shell commands, and reads its secrets from a GitHub Environment restricted to `main`. Anything that runs before a secret is used can otherwise tamper with the runner (git config, `PATH`, environment files) and steal the secret, and the repo is public, its dependencies change, and from M3 its agents read untrusted news. Introduced for the Snapshot deploy key after a security review; it applies to every later secret, including the FPL login.

## Consequences

- The FPL executor can't simply be "the pipeline with a token": the pipeline produces a checked Plan as an artifact, and a minimal job holding the token sends it. That matches the design already: agents never hold credentials ([05](../design/05-execution-and-safety.md)).
- Third-party actions are pinned to commit SHAs, with Dependabot proposing updates.
