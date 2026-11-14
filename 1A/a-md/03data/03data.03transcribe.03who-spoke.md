# 03data.03transcribe Who Spoke

> Attribute words to speakers: diarization for one mixed channel, channel identification for stereo.

## Index

- [1. Diarization Vs Channel Identification](#1-diarization-vs-channel-identification)
- [2. Enabling Speaker Labels](#2-enabling-speaker-labels)
- [3. Channel Turns In The Parser](#3-channel-turns-in-the-parser)

## 1. Diarization Vs Channel Identification

The two are mutually exclusive; choose one per job.

| Option | Setting | Input | Reliability |
|---|---|---|---|
| Speaker diarization | `ShowSpeakerLabels` + `MaxSpeakerLabels` (2–30) | One mixed audio channel | A model; degrades with overlapping speech |
| Channel identification | `ChannelIdentification` | Stereo (agent left, customer right) | Deterministic; more reliable |

Pick: channel identification for stereo calls, unless the audio is mono.

## 2. Enabling Speaker Labels

The code uses diarization because uploads are not guaranteed to be stereo.

```python
# app/infra/_03data_03transcribe.py  (inside start_job)
if diarize:
    # ShowSpeakerLabels and ChannelIdentification are mutually exclusive (we use the former)
    settings["ShowSpeakerLabels"] = True
    settings["MaxSpeakerLabels"] = cfg.max_speakers  # 2..30
```

- **Catch**: setting both raises `BadRequest`
- **Catch**: `diarize` is part of the job name hash
  - Toggling it creates a new job

## 3. Channel Turns In The Parser

When no speaker segments exist, the parser builds one turn per channel.

- Source: `results.channel_labels.channels[]`
- Each channel becomes a turn from its first to last word
- Turns are sorted by start time

```python
# app/domain/_03data_03transcribe.py  (inside parse_transcript)
if not segments:
    for ch in results.get("channel_labels", {}).get("channels", []):
        ch_items = _words(ch.get("items", []))  # pronunciation items only
        if ch_items:
            text = " ".join(i["alternatives"][0]["content"] for i in ch_items)
            turns.append(Turn(ch["channel_label"], float(ch_items[0]["start_time"]), float(ch_items[-1]["end_time"]), text))
    turns.sort(key=lambda t: t.start)
```

- **Catch**: one turn per channel loses back-and-forth order within the call
  - Fine for summaries; split by pause for turn-level analytics
