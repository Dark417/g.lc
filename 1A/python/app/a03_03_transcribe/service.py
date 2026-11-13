"""Use case: audio file -> redacted transcript -> summary."""

from typing import Any

from app.a03_03_transcribe.config import get_transcribe_settings
from app.a03_03_transcribe.infra import read_transcript, start_job, summarize, wait_for_job
from app.shared.config import get_settings


def transcribe_and_summarize(key: str, diarize: bool = True, redact: bool = True) -> dict[str, Any]:
    """Run the full path; failed jobs return the failure reason instead of raising."""
    uri = f"s3://{get_settings().data_bucket}/{get_transcribe_settings().input_prefix}{key}"
    name = start_job(uri, diarize, redact)
    job = wait_for_job(name)
    if job["TranscriptionJobStatus"] == "FAILED":
        return {"job": name, "status": "FAILED", "reason": job.get("FailureReason", "")}
    transcript = read_transcript(name)
    return {"job": name, "status": "COMPLETED", "turns": len(transcript.turns), "summary": summarize(transcript)}
