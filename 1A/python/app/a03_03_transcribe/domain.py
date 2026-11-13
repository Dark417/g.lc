"""Transcript models + parser for the Transcribe output JSON. No SDK imports."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Turn:
    speaker: str
    start: float
    end: float
    text: str


@dataclass
class Transcript:
    text: str
    turns: list[Turn] = field(default_factory=list)


def _words(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [i for i in items if i.get("type") == "pronunciation"]


def parse_transcript(doc: dict[str, Any]) -> Transcript:
    """Build speaker turns from `results`.

    Shapes (Transcribe output JSON):
      results.transcripts[0].transcript
      results.items[]: {type: pronunciation|punctuation, start_time, end_time, alternatives[{content, confidence}], speaker_label?}
      results.speaker_labels.segments[]: {speaker_label, start_time, end_time, items[{start_time, end_time, speaker_label}]}
      results.channel_labels.channels[]: {channel_label, items[...]}  (channel identification)
    Catch: punctuation items carry no times, so attach them to the previous word; times are strings.
    """
    results = doc["results"]
    full = results["transcripts"][0]["transcript"] if results.get("transcripts") else ""
    items: list[dict[str, Any]] = results.get("items", [])
    # Index words by start_time so speaker segments can pick their words.
    content_by_start: dict[str, str] = {}
    for it in items:
        if it.get("type") == "pronunciation" and it.get("alternatives"):
            content_by_start[it["start_time"]] = it["alternatives"][0]["content"]
    turns: list[Turn] = []
    segments = results.get("speaker_labels", {}).get("segments", [])
    for seg in segments:
        words = [content_by_start[w["start_time"]] for w in seg.get("items", []) if w.get("start_time") in content_by_start]
        turns.append(Turn(seg["speaker_label"], float(seg["start_time"]), float(seg["end_time"]), " ".join(words)))
    if not segments:
        for ch in results.get("channel_labels", {}).get("channels", []):
            ch_items = _words(ch.get("items", []))
            if ch_items:
                text = " ".join(i["alternatives"][0]["content"] for i in ch_items)
                turns.append(Turn(ch["channel_label"], float(ch_items[0]["start_time"]), float(ch_items[-1]["end_time"]), text))
        turns.sort(key=lambda t: t.start)
    return Transcript(text=full, turns=turns)


def render_turns(t: Transcript) -> str:
    """Text for an LLM prompt: one line per turn with a timestamp."""
    if not t.turns:
        return t.text
    return "\n".join(f"[{x.start:.0f}s] {x.speaker}: {x.text}" for x in t.turns)
