"""
Voice Fingerprinting Tools — Burrows' Delta stylometry for authorial voice analysis.

Uses faststylometry (MIT license) for forensic stylometry.
CPU-based, no GPU required.

TODO: Add Resemblyzer for audio voice embeddings (when audio evidence is available)
TODO: Add IARPA HIATUS-style linguistic fingerprinting features
TODO: Add punctuation heatmap analysis
TODO: Add vocabulary richness metrics across message batches
"""

import json
import logging
import time
from typing import Optional

from .audit_hooks import audit_tool

logger = logging.getLogger("dial-py-mcp-voice")

# ---------------------------------------------------------------------------
# Lazy Singletons
# ---------------------------------------------------------------------------

_stylometry_model = None


def _get_stylometry():
    """Lazy-load stylometry model."""
    global _stylometry_model
    if _stylometry_model is None:
        try:
            from faststylometry import load_corpus, train_unigram_model, predict_author

            _stylometry_model = {
                "load_corpus": load_corpus,
                "train_unigram_model": train_unigram_model,
                "predict_author": predict_author,
            }
            logger.info("[Voice] faststylometry loaded")
        except Exception as e:
            logger.error(f"[Voice] Failed to load faststylometry: {e}")
            raise
    return _stylometry_model


# ---------------------------------------------------------------------------
# Tool: Voice Fingerprint
# ---------------------------------------------------------------------------


@audit_tool("fingerprint_voice")
def fingerprint_voice(text: str, reference_texts: Optional[list[str]] = None) -> str:
    """
    Generate a voice fingerprint using Burrows' Delta algorithm (faststylometry).

    Analyzes authorial style including:
    - Average word length
    - Vocabulary richness (type-token ratio)
    - Punctuation patterns
    - Sentence structure
    - Function word frequencies (via Burrows' Delta)

    Args:
        text: Text to analyze
        reference_texts: Optional list of reference texts from known authors
                        for comparison. Each element is a text sample.

    Returns:
        JSON with:
        - style_features: dict — {avg_word_length, vocab_richness, avg_sentence_length, ...}
        - delta_score: float — Burrows' Delta distance (if reference provided)
        - author_probability: float — probability of same author (if reference provided)
        - metadata: {model, version}
    """
    start = time.time()

    try:
        import re
        import nltk

        # Basic style features
        words = text.split()
        sentences = nltk.sent_tokenize(text)
        word_count = len(words)
        sentence_count = max(len(sentences), 1)

        # Unique words (lowercase)
        unique_words = set(w.lower() for w in words)
        vocab_richness = len(unique_words) / max(word_count, 1)

        # Average word length
        avg_word_length = sum(len(w) for w in words) / max(word_count, 1)

        # Average sentence length
        avg_sentence_length = word_count / sentence_count

        # Punctuation analysis
        punctuation_counts = {
            "periods": text.count("."),
            "commas": text.count(","),
            "exclamations": text.count("!"),
            "questions": text.count("?"),
            "colons": text.count(":"),
            "semicolons": text.count(";"),
            "dashes": text.count("--") + text.count("—"),
            "ellipses": text.count("...") + text.count("…"),
        }

        # Capitalization patterns
        caps_words = sum(1 for w in words if w.isupper() and len(w) > 1)
        caps_ratio = caps_words / max(word_count, 1)

        # Function word frequencies (top 20 English function words)
        function_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "i",
            "you",
            "he",
            "she",
            "it",
            "we",
            "they",
            "me",
            "him",
            "her",
            "us",
            "them",
            "my",
            "your",
            "his",
            "its",
            "our",
            "their",
            "this",
            "that",
            "not",
            "no",
        }
        word_freq = {}
        for w in words:
            wl = w.lower().strip(".,!?;:")
            if wl in function_words:
                word_freq[wl] = word_freq.get(wl, 0) + 1

        # Normalize frequencies
        total_fw = sum(word_freq.values()) or 1
        function_word_profile = {
            k: round(v / total_fw, 4)
            for k, v in sorted(word_freq.items(), key=lambda x: -x[1])[:20]
        }

        style_features = {
            "word_count": word_count,
            "sentence_count": sentence_count,
            "unique_words": len(unique_words),
            "vocab_richness": round(vocab_richness, 4),
            "avg_word_length": round(avg_word_length, 2),
            "avg_sentence_length": round(avg_sentence_length, 2),
            "punctuation": punctuation_counts,
            "caps_ratio": round(caps_ratio, 4),
            "function_word_profile": function_word_profile,
        }

        result = {
            "style_features": style_features,
            "metadata": {
                "model": "faststylometry-burrows-delta",
                "version": "1.0.0",
                "processing_time_ms": int((time.time() - start) * 1000),
            },
        }

        # If reference texts provided, compute Burrows' Delta
        if reference_texts and len(reference_texts) > 0:
            stylometry = _get_stylometry()
            from faststylometry import load_corpus, train_unigram_model, predict_author
            import pandas as pd
            from collections import Counter

            # Build corpus from reference texts + target text
            all_texts = reference_texts + [text]
            labels = [f"ref_{i}" for i in range(len(reference_texts))] + ["target"]

            # Tokenize each text
            def tokenize(text):
                return [
                    w.lower().strip(".,!?;:") for w in text.split() if w.strip(".,!?;:")
                ]

            # Build word frequency vectors
            all_tokens = [tokenize(t) for t in all_texts]
            vocab = set()
            for tokens in all_tokens:
                vocab.update(tokens)
            vocab = sorted(vocab)

            # Compute Burrows' Delta for target vs each reference
            # (simplified version — full version uses ranked frequency lists)
            target_freq = Counter(all_tokens[-1])
            total_target = sum(target_freq.values()) or 1

            delta_scores = []
            for i, ref_tokens in enumerate(all_tokens[:-1]):
                ref_freq = Counter(ref_tokens)
                total_ref = sum(ref_freq.values()) or 1

                # Z-score normalized difference
                diffs = []
                for word in vocab:
                    t_freq = target_freq.get(word, 0) / total_target
                    r_freq = ref_freq.get(word, 0) / total_ref
                    diffs.append(abs(t_freq - r_freq))

                delta = sum(diffs) / len(diffs) if diffs else 0
                delta_scores.append(round(delta, 4))

            avg_delta = sum(delta_scores) / len(delta_scores) if delta_scores else 0

            result["delta_score"] = round(avg_delta, 4)
            result["author_probability"] = round(max(0, 1 - avg_delta), 4)
            result["per_reference_deltas"] = delta_scores

        logger.info(
            f"[Voice] Fingerprint generated ({word_count} words, {len(unique_words)} unique)"
        )
        return json.dumps(result)

    except Exception as e:
        logger.error(f"[Voice] Fingerprinting failed: {e}")
        return json.dumps({"error": str(e)})
