# Parsing, Timeline, and Evidence-Processing Tools

This page covers the staged parsing and timeline-oriented subtrees inside `tools/utilities/`.

## NLP_Tools

- **Path**: `tools/utilities/NLP_Tools`
- **Why it matters**: bundles NLP, RAG, and analysis-oriented source material.
- **Potential fit**: reference set for text analysis and retrieval layers.

## parsers

- **Path**: `tools/utilities/parsers`
- **Why it matters**: groups takeout, social export, and chat-export parsers by source family.
- **Potential fit**: ingestion reference library for cross-platform export normalization.

## TimelineExtractor

- **Path**: `tools/utilities/TimelineExtractor`
- **What it is**: Python tool for extracting Google Maps Timeline location history.
- **Why it matters**: time-and-location reconstruction is central to evidence correlation.
- **Potential fit**: timeline ingestion sidecar or reference parser for location evidence.
- **Local sources**: `README.md`, `src/`, `requirements.txt`

## Timeline_Tools

- **Path**: `tools/utilities/Timeline_Tools`
- **Why it matters**: groups multiple timeline viewers and extractors.
- **Potential fit**: reference bundle for timeline reconstruction and analyst review.

Sources: `tools/utilities/NLP_Tools`, `tools/utilities/parsers`, `tools/utilities/TimelineExtractor/README.md`, `tools/utilities/Timeline_Tools`
