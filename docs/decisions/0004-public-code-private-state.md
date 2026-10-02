# Public code, private state, public Snapshots

The code repo is public, mainly so GitHub Actions minutes are free (the scheduled jobs need far more than the 2,000 free private minutes) and recruiters can read it. Because anything committed is public, the agent's private state (paused runs, Plans, Lessons, Instructions, Chat history, Shadow Team results) lives in a free hosted Postgres database, which is also LangGraph's supported checkpoint store. Raw Snapshots go to a separate public data repo, which keeps the database small and publishes a free FPL dataset.

## Considered Options

- Commit all state to git: free and simple, but would publish every Memo and Chat.
- Cache state between Actions jobs: free, but caches can be evicted and a paused run lost.
