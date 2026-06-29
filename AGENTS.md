# AGENTS.md

## Local skills

Repo-scoped skills live in `.agents/skills/<name>/SKILL.md` (tool-agnostic, not tied to any single agent runtime). opencode loads them via `skills.paths` in `.opencode/opencode.json`.

## Pre-commit checks

Before `git commit`, run `uv run prek run --all-files` and resolve anything reported. Do not commit if checks fail. This replaces the previous automatic Stop hook.

## Agent skills

### Issue tracker

Issues and PRDs live as markdown files under `.scratch/<feature-slug>/`. See `docs/agents/issue-tracker.md`.

### Triage labels

Default canonical role strings (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: `CONTEXT.md` and `docs/adr/` at the repo root. See `docs/agents/domain.md`.
