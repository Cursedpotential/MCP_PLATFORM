"""
DPK Pre-Processing Tools — IBM Data Prep Kit transforms wrapped as MCP tools.

These tools run FIRST on raw text, before any custom detection.
They provide: HAP scoring, PII redaction, language ID, doc quality, readability.

All tools follow the standard interface:
- Input: text (str), optional context, mode (pass1/pass2)
- Output: JSON with score, categories, confidence, evidence, metadata

TODO: Fine-tune HAP model on custody-specific data (Colab Pro)
TODO: Investigate IBM Cloud free tier for heavy workloads (HAP 125m model)
TODO: Add doc_chunk tool once DPK doc_chunk API is confirmed
TODO: Add text_encoder tool for embedding generation via DPK
"""

import json
import logging
import os
import time
from typing import Optional

from .audit_hooks import audit_tool

logger = logging.getLogger("dial-py-mcp-dpk")

# ---------------------------------------------------------------------------
# Lazy Singletons (following existing server.py pattern)
# ---------------------------------------------------------------------------

_hap_transform = None
_pii_analyzer = None
_lang_id_model = None
_doc_quality_scorer = None
_readability_calculator = None


def _get_hap():
    """Lazy-load HAP transform (IBM Granite 38M model)."""
    global _hap_transform
    if _hap_transform is None:
        try:
            from dpk_hap.transform import HAPTransform

            _hap_transform = HAPTransform(
                {
                    "model_name_or_path": "ibm-granite/granite-guardian-hap-38m",
                    "annotation_column": "hap_score",
                    "doc_text_column": "contents",
                    "max_length": 512,
                    "batch_size": 128,
                }
            )
            logger.info("[DPK] HAP transform loaded (granite-guardian-hap-38m)")
        except Exception as e:
            logger.error(f"[DPK] Failed to load HAP: {e}")
            raise
    return _hap_transform


def _get_pii_analyzer():
    """Lazy-load PII analyzer (Microsoft Presidio + Flair NER)."""
    global _pii_analyzer
    if _pii_analyzer is None:
        try:
            from presidio_analyzer import AnalyzerEngine
            from presidio_analyzer.nlp_engine import NlpEngineProvider

            # Configure with spaCy
            nlp_config = {
                "nlp_engine_name": "spacy",
                "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}],
            }
            nlp_engine = NlpEngineProvider(nlp_configuration=nlp_config).create_engine()
            _pii_analyzer = AnalyzerEngine(nlp_engine=nlp_engine)
            logger.info("[DPK] PII analyzer loaded (Presidio + spaCy)")
        except Exception as e:
            logger.error(f"[DPK] Failed to load PII analyzer: {e}")
            raise
    return _pii_analyzer


def _get_lang_id():
    """Lazy-load language identification model (fasttext)."""
    global _lang_id_model
    if _lang_id_model is None:
        try:
            import fasttext

            # Download lid.176.bin if not present
            model_path = os.path.expanduser("~/.cache/fasttext/lid.176.bin")
            if not os.path.exists(model_path):
                os.makedirs(os.path.dirname(model_path), exist_ok=True)
                import urllib.request

                url = "https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin"
                urllib.request.urlretrieve(url, model_path)
            _lang_id_model = fasttext.load_model(model_path)
            logger.info("[DPK] Language ID model loaded (fasttext lid.176)")
        except Exception as e:
            logger.error(f"[DPK] Failed to load lang-id: {e}")
            raise
    return _lang_id_model


# ---------------------------------------------------------------------------
# Tool: HAP Score
# ---------------------------------------------------------------------------


@audit_tool("dpk_hap_score")
def dpk_hap_score(text: str, mode: str = "pass1") -> str:
    """
    Score text for Hate, Abuse, and Profanity (HAP) using IBM Granite 38M model.

    The HAP transform splits text into sentences, scores each 0-1,
    and returns the maximum score as the document score.

    Args:
        text: Text to analyze
        mode: "pass1" (blind) or "pass2" (hindsight) — affects context window

    Returns:
        JSON with:
        - score: float (0-1) — max HAP score across sentences
        - sentence_scores: list[float] — per-sentence HAP scores
        - categories: ["hap"] or ["clean"]
        - confidence: float
        - metadata: {model, version, mode}
    """
    start = time.time()

    try:
        hap = _get_hap()
        # Clean text for processing
        clean_text = " ".join(text.strip().splitlines())

        # Process through HAP model
        # Note: HAPTransform.transform expects a PyArrow table
        # For single text, we use the underlying model directly
        import torch
        import nltk

        # Sentence splitting
        sentences = nltk.sent_tokenize(clean_text)
        if not sentences:
            return json.dumps(
                {
                    "score": 0.0,
                    "sentence_scores": [],
                    "categories": ["clean"],
                    "confidence": 1.0,
                    "metadata": {"model": "granite-guardian-hap-38m", "mode": mode},
                }
            )

        # Score each sentence
        # Access the model internals from the transform
        tokenizer = hap.tokenizer
        model = hap.model
        device = next(model.parameters()).device

        inputs = tokenizer(
            sentences,
            max_length=512,
            padding=True,
            truncation=True,
            return_tensors="pt",
        ).to(device)

        with torch.no_grad():
            logits = model(**inputs).logits
            scores = torch.softmax(logits, dim=1).cpu().numpy()[:, 1].tolist()

        max_score = max(scores) if scores else 0.0
        categories = ["hap"] if max_score > 0.5 else ["clean"]

        result = {
            "score": round(max_score, 4),
            "sentence_scores": [round(s, 4) for s in scores],
            "categories": categories,
            "confidence": round(max_score, 4),
            "metadata": {
                "model": "granite-guardian-hap-38m",
                "version": "1.0.0",
                "mode": mode,
                "sentence_count": len(sentences),
                "processing_time_ms": int((time.time() - start) * 1000),
            },
        }

        logger.info(f"[DPK] HAP score: {max_score:.4f} ({len(sentences)} sentences)")
        return json.dumps(result)

    except Exception as e:
        logger.error(f"[DPK] HAP scoring failed: {e}")
        return json.dumps({"error": str(e), "score": None})


# ---------------------------------------------------------------------------
# Tool: PII Redact
# ---------------------------------------------------------------------------


@audit_tool("dpk_pii_redact")
def dpk_pii_redact(
    text: str,
    entities: Optional[list[str]] = None,
    operator: str = "replace",
    score_threshold: float = 0.6,
) -> str:
    """
    Detect and redact Personally Identifiable Information (PII) using Microsoft Presidio.

    Args:
        text: Text to analyze
        entities: List of entity types to detect (default: all supported)
        operator: "replace" (with placeholder) or "redact" (remove)
        score_threshold: Minimum confidence score (0-1)

    Returns:
        JSON with:
        - redacted_text: str — text with PII replaced/removed
        - detected_pii: list[dict] — [{type, text, start, end, confidence}]
        - pii_entity_types: list[str] — unique entity types found
        - pii_count: int — total PII entities found
        - metadata: {model, operator, threshold}
    """
    start = time.time()

    default_entities = [
        "PERSON",
        "EMAIL_ADDRESS",
        "PHONE_NUMBER",
        "CREDIT_CARD",
        "LOCATION",
        "DATE_TIME",
    ]
    target_entities = entities or default_entities

    try:
        analyzer = _get_pii_analyzer()
        from presidio_analyzer import RecognizerResult

        # Analyze text
        results = analyzer.analyze(
            text=text,
            entities=target_entities,
            language="en",
            score_threshold=score_threshold,
        )

        # Build detected PII list
        detected_pii = []
        for r in results:
            detected_pii.append(
                {
                    "type": r.entity_type,
                    "text": text[r.start : r.end],
                    "start": r.start,
                    "end": r.end,
                    "confidence": round(r.score, 4),
                }
            )

        # Apply redaction (process in reverse order to preserve positions)
        redacted_text = text
        if operator == "replace":
            for r in sorted(results, key=lambda x: x.start, reverse=True):
                redacted_text = (
                    redacted_text[: r.start]
                    + f"<{r.entity_type}>"
                    + redacted_text[r.end :]
                )
        elif operator == "redact":
            for r in sorted(results, key=lambda x: x.start, reverse=True):
                redacted_text = (
                    redacted_text[: r.start] + "[REDACTED]" + redacted_text[r.end :]
                )

        entity_types = list(set(r.entity_type for r in results))

        result = {
            "redacted_text": redacted_text,
            "detected_pii": detected_pii,
            "pii_entity_types": entity_types,
            "pii_count": len(detected_pii),
            "metadata": {
                "model": "presidio+spacy",
                "operator": operator,
                "threshold": score_threshold,
                "processing_time_ms": int((time.time() - start) * 1000),
            },
        }

        logger.info(
            f"[DPK] PII detected: {len(detected_pii)} entities ({entity_types})"
        )
        return json.dumps(result)

    except Exception as e:
        logger.error(f"[DPK] PII redaction failed: {e}")
        return json.dumps({"error": str(e)})


# ---------------------------------------------------------------------------
# Tool: Language ID
# ---------------------------------------------------------------------------


@audit_tool("dpk_lang_id")
def dpk_lang_id(text: str) -> str:
    """
    Identify the language of text using fasttext.

    Args:
        text: Text to identify

    Returns:
        JSON with:
        - language: str — ISO 639-1 language code (e.g., "en", "es", "fr")
        - confidence: float (0-1)
        - metadata: {model, version}
    """
    start = time.time()

    try:
        model = _get_lang_id()
        # fasttext expects single line, no newlines
        clean_text = " ".join(text.strip().splitlines())[:1000]  # Limit for speed

        predictions = model.predict(clean_text, k=1)
        lang_code = predictions[0][0].replace("__label__", "")
        confidence = float(predictions[1][0])

        result = {
            "language": lang_code,
            "confidence": round(confidence, 4),
            "metadata": {
                "model": "fasttext-lid-176",
                "version": "1.0.0",
                "processing_time_ms": int((time.time() - start) * 1000),
            },
        }

        logger.info(f"[DPK] Language detected: {lang_code} ({confidence:.2%})")
        return json.dumps(result)

    except Exception as e:
        logger.error(f"[DPK] Language ID failed: {e}")
        return json.dumps({"error": str(e)})


# ---------------------------------------------------------------------------
# Tool: Doc Quality
# ---------------------------------------------------------------------------


@audit_tool("dpk_doc_quality")
def dpk_doc_quality(text: str) -> str:
    """
    Score document quality based on multiple metrics.

    Args:
        text: Text to analyze

    Returns:
        JSON with:
        - score: float (0-1) — overall quality score
        - metrics: dict — individual quality metrics
        - metadata: {model, version}
    """
    start = time.time()

    try:
        words = text.split()
        sentences = text.split(".")

        # Basic quality metrics
        word_count = len(words)
        sentence_count = len([s for s in sentences if s.strip()])
        avg_word_length = sum(len(w) for w in words) / max(word_count, 1)
        avg_sentence_length = word_count / max(sentence_count, 1)

        # Quality heuristics
        has_structure = any(c in text for c in [".", "!", "?", ":"])
        has_punctuation = any(c in text for c in [",", ".", ";", ":"])
        not_too_short = word_count >= 5
        not_all_caps = not text.isupper()

        quality_score = sum(
            [
                0.25 if has_structure else 0,
                0.25 if has_punctuation else 0,
                0.25 if not_too_short else 0,
                0.25 if not_all_caps else 0,
            ]
        )

        result = {
            "score": round(quality_score, 4),
            "metrics": {
                "word_count": word_count,
                "sentence_count": sentence_count,
                "avg_word_length": round(avg_word_length, 2),
                "avg_sentence_length": round(avg_sentence_length, 2),
                "has_structure": has_structure,
                "has_punctuation": has_punctuation,
            },
            "metadata": {
                "model": "dpk-doc-quality",
                "version": "1.0.0",
                "processing_time_ms": int((time.time() - start) * 1000),
            },
        }

        logger.info(f"[DPK] Doc quality: {quality_score:.2f} ({word_count} words)")
        return json.dumps(result)

    except Exception as e:
        logger.error(f"[DPK] Doc quality failed: {e}")
        return json.dumps({"error": str(e)})


# ---------------------------------------------------------------------------
# Tool: Readability
# ---------------------------------------------------------------------------


@audit_tool("dpk_readability")
def dpk_readability(text: str) -> str:
    """
    Calculate readability metrics for text.

    Args:
        text: Text to analyze

    Returns:
        JSON with:
        - flesch_reading_ease: float (0-100, higher = easier)
        - flesch_kincaid_grade: float (US grade level)
        - avg_sentence_length: float
        - avg_syllables_per_word: float
        - metadata: {model, version}
    """
    start = time.time()

    try:
        import re

        words = text.split()
        sentences = [s for s in text.split(".") if s.strip()]

        word_count = len(words)
        sentence_count = max(len(sentences), 1)

        # Simple syllable counting
        def count_syllables(word):
            word = word.lower()
            count = len(re.findall(r"[aeiouy]+", word))
            return max(count, 1)

        syllable_count = sum(count_syllables(w) for w in words)

        avg_sentence_length = word_count / sentence_count
        avg_syllables_per_word = syllable_count / max(word_count, 1)

        # Flesch Reading Ease
        fre = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        fre = max(0, min(100, fre))  # Clamp to 0-100

        # Flesch-Kincaid Grade Level
        fkgl = (0.39 * avg_sentence_length) + (11.8 * avg_syllables_per_word) - 15.59
        fkgl = max(0, fkgl)  # No negative grades

        result = {
            "flesch_reading_ease": round(fre, 2),
            "flesch_kincaid_grade": round(fkgl, 2),
            "avg_sentence_length": round(avg_sentence_length, 2),
            "avg_syllables_per_word": round(avg_syllables_per_word, 2),
            "word_count": word_count,
            "sentence_count": sentence_count,
            "metadata": {
                "model": "dpk-readability",
                "version": "1.0.0",
                "processing_time_ms": int((time.time() - start) * 1000),
            },
        }

        logger.info(f"[DPK] Readability: FRE={fre:.1f}, FKGL={fkgl:.1f}")
        return json.dumps(result)

    except Exception as e:
        logger.error(f"[DPK] Readability failed: {e}")
        return json.dumps({"error": str(e)})
