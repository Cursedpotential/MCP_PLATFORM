# Loose Tool Files

These top-level files in `tools/utilities/` look like downloaded libraries, binary wrappers, or loose source assets rather than structured local projects.

## Current Records

- `10x-patterns`
- `MinerU`
- `TakeoutsTimelining`
- `ai-json-fixer`
- `gog`
- `judicAIta`
- `mdp`
- `ontology`
- `partial-json-parser-kmp`
- `transform-x`

## Why They Matter

- They may still contain useful upstream binaries, scripts, or references.
- They are easy to lose track of because they are not self-describing directories.
- They should be documented as staged assets so they can be promoted, wrapped, or archived deliberately.

## Current Recommendation

- Keep them locally referenced in the manifest.
- Do not treat them as active product dependencies yet.
- Promote any one of them only after identifying provenance, runtime expectations, and application fit.

Sources: `tools/utilities`
