---
description: Run pre-commit checks (prek) on staged files.
agent: build
---
Run the repo's pre-commit checks against the currently staged files and report results. Do not auto-fix; show me what failed.

```
uv run prek run --all-authors --files $(git diff --cached --name-only)
```

If nothing is staged, say so and stop. If checks pass, say "clean" and stop.