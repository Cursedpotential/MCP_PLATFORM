# Gitignore Hardening Spec (2026-04-08)

## Goal
Prevent accidental commits of secrets, local runtime state, and build/cache artifacts in the dial-stack workspace.

## Scope
- Root `.gitignore`
- `client/.gitignore`

## Changes
- Added broader secret patterns (`*.env`, key/cert formats).
- Added runtime/log/temp artifacts (`*.out`, `*.err`, `*.temp`, swap/backups).
- Added Python/coverage caches (`.pytest_cache`, `.mypy_cache`, `.coverage*`, `coverage/`, `htmlcov/`).
- Added local DB/runtime artifacts (`*.db`, `*.sqlite*`, `*.duckdb`, `*.wal`, `*.shm`, `*.pid`).
- Added client-specific coverage/TS cache ignore patterns.

## Expected Outcome
- Cleaner commits with lower risk of credential or local-state leakage.
- Reduced noisy diffs from generated files.

## Validation
- `git status` only shows intended tracked source/spec changes after initialization.
