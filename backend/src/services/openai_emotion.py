from __future__ import annotations

import base64
import json
from typing import Any

from openai import OpenAI, OpenAIError

from ..config import OPENAI_API_KEY, OPENAI_MODEL_TEXT, OPENAI_MODEL_VISION
from ..emotion.text_emotion import detect_text_emotion
from ..emotion.image_emotion import detect_image_emotion

EMOTIONS = {"happy", "sad", "calm", "angry", "surprised", "fearful", "neutral"}


def _normalize_emotion(emotion: str) -> str:
    cleaned = emotion.strip().lower()
    if cleaned in EMOTIONS:
        return cleaned

    aliases = {
        "joy": "happy",
        "sadness": "sad",
        "anger": "angry",
        "fear": "fearful",
        "surprise": "surprised",
    }
    return aliases.get(cleaned, "neutral")


def _extract_json(text: str) -> dict[str, Any]:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return {}
    try:
        return json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return {}


def detect_emotion_from_text(text: str) -> dict[str, Any]:
    if not OPENAI_API_KEY:
        fallback = detect_text_emotion(text)
        return {
            "emotion": _normalize_emotion(fallback.emotion),
            "confidence": fallback.confidence,
            "analysis": "Fallback NLP used because OPENAI_API_KEY is not configured.",
            "provider": "fallback",
        }

    client = OpenAI(api_key=OPENAI_API_KEY)
    prompt = (
        "Classify the user's emotion from this text into exactly one of these emotions: "
        "happy, sad, calm, angry, surprised, fearful, neutral. "
        "Choose the single best matching emotion. "
        "Return strict JSON with keys: emotion, confidence, analysis. "
        "Be consistent - the same text should always get the same emotion."
    )
    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL_TEXT,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": text},
            ],
            temperature=0,  # Make responses deterministic
            seed=42,  # For reproducible results
        )
        raw_text = response.choices[0].message.content
        parsed = _extract_json(raw_text)
        emotion = _normalize_emotion(str(parsed.get("emotion", "neutral")))
        confidence = float(parsed.get("confidence", 0.75))
        analysis = str(parsed.get("analysis", "Emotion extracted from text."))
        return {
            "emotion": emotion,
            "confidence": max(0.0, min(confidence, 1.0)),
            "analysis": analysis,
            "provider": "openai",
        }
    except (OpenAIError, Exception):
        fallback = detect_text_emotion(text)
        return {
            "emotion": _normalize_emotion(fallback.emotion),
            "confidence": fallback.confidence,
            "analysis": "Fallback NLP used because OpenAI request failed.",
            "provider": "fallback",
        }


def detect_emotion_from_image_bytes(image_bytes: bytes, filename: str) -> dict[str, Any]:
    if not OPENAI_API_KEY:
        local_result = detect_image_emotion(image_bytes)
        return {
            "emotion": _normalize_emotion(local_result["emotion"]),
            "confidence": local_result["confidence"],
            "analysis": local_result["analysis"],
            "provider": "local-deepface",
        }

    mime = "image/jpeg"
    name_lower = filename.lower()
    if name_lower.endswith(".png"):
        mime = "image/png"
    elif name_lower.endswith(".webp"):
        mime = "image/webp"

    encoded = base64.b64encode(image_bytes).decode("utf-8")
    data_url = f"data:{mime};base64,{encoded}"

    client = OpenAI(api_key=OPENAI_API_KEY)
    prompt = (
        "Analyze the facial expression in this image and detect exactly one primary emotion from: "
        "happy, sad, calm, angry, surprised, fearful, neutral. "
        "Choose the single most dominant emotion based on facial features. "
        "Return strict JSON with keys: emotion, confidence, analysis. "
        "Be consistent - the same image should always get the same emotion."
    )
    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL_VISION,
            messages=[
                {"role": "system", "content": prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Analyze this face and detect emotion."},
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ],
                },
            ],
            temperature=0,  # Make responses deterministic
            seed=42,  # For reproducible results
        )
        raw_text = response.choices[0].message.content
        parsed = _extract_json(raw_text)
        emotion = _normalize_emotion(str(parsed.get("emotion", "neutral")))
        confidence = float(parsed.get("confidence", 0.75))
        analysis = str(parsed.get("analysis", "Emotion extracted from image."))
        return {
            "emotion": emotion,
            "confidence": max(0.0, min(confidence, 1.0)),
            "analysis": analysis,
            "provider": "openai",
        }
    except (OpenAIError, Exception):
        local_result = detect_image_emotion(image_bytes)
        return {
            "emotion": _normalize_emotion(local_result["emotion"]),
            "confidence": local_result["confidence"],
            "analysis": "Fallback image analysis used because OpenAI request failed.",
            "provider": "fallback",
        }
