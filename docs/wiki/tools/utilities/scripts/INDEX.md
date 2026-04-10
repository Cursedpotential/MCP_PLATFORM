# Utilities Script Pack

This section covers `tools/utilities/scripts/`, which is the active operational script pack inside the intake library.

## Status

- Pack status: `active`
- Duplicate files with ` (2)` suffix: `redundant`
- Helper tests and payloads: `evaluate`

## Canonical High-Value Scripts

- `chatgpt_parser.py`
- `conversation_splitter.py`
- `conversation_to_docx.py`
- `find_duplicates.py`
- `forensic_diff.py`
- `output_schemas.py`
- `pandoc_converter.py`
- `robust_conversation_extractor.py`
- `analyze_triggers.py`

These already have older per-script wiki pages under [utility](/mnt/c/Users/matts/Projects/TheBigOne/dial-stack/docs/wiki/tools/utility/INDEX.md). The authoritative intake status now lives in the utilities manifest.

## Additional Script Groups

- `python-tools/`: Semantica-oriented support package for pipeline, memory service, and dataset loading
- PDF and markdown conversion helpers
- JSON split/merge helpers
- database and Supabase helpers
- test and verification scripts

## Duplicate Handling

Files named like `tool_name (2).py` are duplicate copies and should not be treated as canonical. The manifest marks these as `redundant`.

Sources: `tools/utilities/scripts`, `docs/wiki/tools/utility/INDEX.md`
