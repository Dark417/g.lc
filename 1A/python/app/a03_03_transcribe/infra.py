"""Transcribe SDK calls: start (idempotent), poll, read transcript, summarize with Bedrock."""

import hashlib
import json
import time
from typing import Any

from botocore.exceptions import ClientError

from app.a03_03_transcribe.config import get_transcribe_settings
from app.a03_03_transcribe.domain import Transcript, parse_transcript, render_turns
from app.shared.aws import client
from app.shared.config import get_settings
from app.shared.retry import backoff

_MEDIA_FORMATS = {"mp3", "mp4", "wav", "flac", "ogg", "amr", "webm", "m4a"}


def job_name_for(media_uri: str, diarize: bool, redact: bool) -> str:
    """Deterministic job name: same media + same options = same name = retry-safe.

    Job names are unique per account+Region; allowed chars are letters, digits, . _ -; max 200.
    Catch: change an option and the name changes; delete old jobs before re-running the same name.
    """
    digest = hashlib.sha256(f"{media_uri}|{diarize}|{redact}".encode()).hexdigest()[:24]
    return f"{get_transcribe_settings().job_prefix}{digest}"


def start_job(media_uri: str, diarize: bool = True, redact: bool = True) -> str:
    """Start (or find) a batch job with vocabulary, filter, speaker labels and PII redaction; returns the job name.

    Catch: a repeated name raises ConflictException; we treat it as 'already started'.
    ShowSpeakerLabels and ChannelIdentification are mutually exclusive (we use the former).
    """
    cfg = get_transcribe_settings()
    name = job_name_for(media_uri, diarize, redact)
    settings: dict[str, Any] = {
        "VocabularyName": cfg.vocabulary_name,  # custom vocabulary (must be READY)
        "VocabularyFilterName": cfg.filter_name,
        "VocabularyFilterMethod": cfg.filter_method,  # mask | remove | tag
    }
    if diarize:
        settings["ShowSpeakerLabels"] = True
        settings["MaxSpeakerLabels"] = cfg.max_speakers  # 2..30
    kwargs: dict[str, Any] = {
        "TranscriptionJobName": name,
        "LanguageCode": cfg.language_code,  # or IdentifyLanguage=True (+LanguageOptions); exclusive
        "Media": {"MediaFileUri": media_uri},
        "OutputBucketName": get_settings().data_bucket,
        "OutputKey": f"{cfg.output_prefix}{name}.json",  # a key ending in / means a folder, else a file name
        # OutputEncryptionKMSKeyId="arn:aws:kms:...",  # SSE-KMS for the transcript; caller needs kms perms
        "Settings": settings,
    }
    ext = media_uri.rsplit(".", 1)[-1].lower()
    if ext in _MEDIA_FORMATS:
        kwargs["MediaFormat"] = ext  # optional: Transcribe can detect it
    if redact:
        kwargs["ContentRedaction"] = {
            "RedactionType": "PII",  # the only value
            "RedactionOutput": cfg.redaction_output,  # redacted | redacted_and_unredacted
            "PiiEntityTypes": [t.strip() for t in cfg.pii_entity_types.split(",")],
        }
    try:
        client("transcribe").start_transcription_job(**kwargs)
    except ClientError as e:
        if e.response["Error"]["Code"] != "ConflictException":
            raise
    return name


def wait_for_job(name: str) -> dict[str, Any]:
    """Poll GetTranscriptionJob (QUEUED, IN_PROGRESS, COMPLETED, FAILED) with backoff; returns the job dict."""
    end = time.monotonic() + get_transcribe_settings().poll_deadline_s
    attempt = 0
    while True:
        job = client("transcribe").get_transcription_job(TranscriptionJobName=name)["TranscriptionJob"]
        if job["TranscriptionJobStatus"] in ("COMPLETED", "FAILED"):
            return job
        if time.monotonic() >= end:
            raise TimeoutError(f"{name} still {job['TranscriptionJobStatus']}")
        time.sleep(backoff(attempt, base=2.0, cap=30.0))
        attempt += 1


def read_transcript(name: str) -> Transcript:
    """Read the transcript JSON we asked Transcribe to write into our bucket, and parse it."""
    cfg = get_transcribe_settings()
    key = f"{cfg.output_prefix}{name}.json"
    body = client("s3").get_object(Bucket=get_settings().data_bucket, Key=key)["Body"].read()
    return parse_transcript(json.loads(body))


def summarize(transcript: Transcript, max_tokens: int = 500) -> str:
    """Summarize with Bedrock Converse (fast model). Use for short calls; window and reduce for long ones.

    Catch: send the REDACTED transcript only; temperature 0 keeps summaries stable.
    """
    resp = client("bedrock-runtime").converse(
        modelId=get_settings().fast_model_id,
        system=[{"text": "Summarize the call in 5 bullets and list action items. Do not invent facts."}],
        messages=[{"role": "user", "content": [{"text": render_turns(transcript)}]}],
        inferenceConfig={"maxTokens": max_tokens, "temperature": 0.0},
    )
    return resp["output"]["message"]["content"][0]["text"]
