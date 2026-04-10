# SBV

## Overview

- **Item**: `tools/utilities/sbv-main`
- **Status**: `integrate`
- **Category**: `application`
- **Source type**: `vendored`
- **Runtime**: Go backend plus React/Vite frontend

SBV is the SMS Backup Viewer application. It imports XML files created by SMS Backup & Restore and presents SMS, MMS, and call-log data through a web interface.

## Why It Matters

- It directly fits the evidence-processing domain.
- It already handles SMS Backup & Restore XML, which is a concrete input format in this workspace.
- It gives a user-facing browser workflow instead of only parser output or backend services.
- It is a stronger immediate integration candidate than most intake items because it is already a complete application.

## Deployment Model

- Backend: Go with SQLite
- Frontend: React with Vite and Bootstrap
- Data model: one SQLite database per user
- Deployment options shown in upstream docs: Docker, Docker Compose, or local development workflow

## Input and Evidence Fit

- Primary input: SMS Backup & Restore XML exports
- Evidence value: SMS, MMS, call logs, inline media, search, analytics, and conversation browsing
- Likely fit in this repo: SMS evidence review, XML parser validation, and human review workflow support

## Integration Direction

Current recommendation:

- Keep SBV as a standalone utility application first
- Document it in the intake catalog as the primary near-term integration target
- Decide later whether to:
  - embed it as a review-sidecar app
  - wrap portions of its import pipeline
  - expose selected capabilities through MCP or another controlled interface

## Key Entry Points

- `README.md`
- `go.mod`
- `frontend/package.json`
- `DEVELOPMENT.md`

## Notes

- This is not a script pack and not an MCP server.
- It should be treated as a full application candidate.
- SMS/XML-related parser docs should cross-link back here when discussing review or browsing workflows.

Sources: `tools/utilities/sbv-main/README.md`, `tools/utilities/sbv-main/go.mod`, `tools/utilities/sbv-main/frontend/package.json`, `tools/utilities/sbv-main/DEVELOPMENT.md`
