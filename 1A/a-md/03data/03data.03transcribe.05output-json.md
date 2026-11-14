# 03data.03transcribe Output JavaScript Object Notation (JSON)

> The transcript JavaScript Object Notation (JSON) shape and how the parser turns it into speaker turns.

## Index

- [1. Shape](#1-shape)
- [2. Parsing Speaker Turns](#2-parsing-speaker-turns)
- [3. Reading From Simple Storage Service (S3)](#3-reading-from-simple-storage-service-s3)

## 1. Shape

All useful content sits under `results`.

- `results.transcripts[0].transcript`: full text
- `results.items[]`: word or punctuation
  - `type`: `pronunciation` or `punctuation`
  - `start_time`, `end_time`
  - `alternatives[{content, confidence}]`
  - `speaker_label` when diarized
- `results.speaker_labels.segments[]`: speaker turns
  - `start_time`, `end_time`, items
- `results.channel_labels.channels[]`: for channel identification
- Timestamps are strings in seconds

```python
# app/domain/_03data_03transcribe.py
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
```

- **Catch**: punctuation items carry no times
  - Attach them to the previous word

## 2. Parsing Speaker Turns

The parser indexes words by start time, then lets each speaker segment pick its words.

→ Read the full text  
→ Map `start_time` → word for pronunciation items  
→ For each speaker segment, collect its words by start time  
→ No segments ⇒ fall back to channel labels ([03 Who Spoke](03data.03transcribe.03who-spoke.md#3-channel-turns-in-the-parser))

```python
# app/domain/_03data_03transcribe.py
def parse_transcript(doc: dict[str, Any]) -> Transcript:
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
    # ... channel fallback when there are no segments
    return Transcript(text=full, turns=turns)
```

- **Catch**: times are strings
  - Use them as dict keys as-is; convert to `float` only for output

## 3. Reading From Simple Storage Service (S3)

The job wrote to a known key, so reading needs no lookup.

```python
# app/infra/_03data_03transcribe.py
def read_transcript(name: str) -> Transcript:
    cfg = get_transcribe_settings()
    key = f"{cfg.output_prefix}{name}.json"  # same key start_job passed as OutputKey
    body = client("s3").get_object(Bucket=get_settings().data_bucket, Key=key)["Body"].read()
    return parse_transcript(json.loads(body))
```

- **Catch**: with `redacted_and_unredacted`, make sure you read the redacted file
