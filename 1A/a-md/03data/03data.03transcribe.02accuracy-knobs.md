# 03data.03transcribe Accuracy Knobs

> Domain adaptation without training: custom vocabulary, vocabulary filters, and language identification.

## Index

- [1. Custom Vocabulary](#1-custom-vocabulary)
- [2. Vocabulary Filter](#2-vocabulary-filter)
- [3. Language Identification](#3-language-identification)
- [4. Output Location And Settings](#4-output-location-and-settings)

## 1. Custom Vocabulary

A custom vocabulary teaches Transcribe your product names and jargon in minutes.

- A list of phrases: product names, jargon
  - Use hyphens for multi-word terms
- Cheap and instant; no training
- Must be `READY` before a job can use it
- Larger accuracy lift: custom language models (CLM)
  - Not coded
  - Needs training data
- Vocabulary first (hours of work saved); CLM only when measured Word Error Rate (WER) stays high

```python
# app/infra/_03data_03transcribe.py  (inside start_job)
settings: dict[str, Any] = {
    "VocabularyName": cfg.vocabulary_name,  # custom vocabulary (must be READY)
    "VocabularyFilterName": cfg.filter_name,
    "VocabularyFilterMethod": cfg.filter_method,  # mask | remove | tag
}
```

- **Catch**: a `PENDING` or `FAILED` vocabulary breaks the job
  - Check `GetVocabulary`
  - Wait for READY; fix the phrase format
- **Catch**: measure WER before and after on a golden set

## 2. Vocabulary Filter

A vocabulary filter acts on listed words in the text output.

- `mask`: replaces with `***`
- `remove`: drops the word
- `tag`: flags the word, keeps the text
- Filters text output only

```python
# app/config/_03data_03transcribe.py
class TranscribeSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="A_TRANSCRIBE_", env_file=".env", extra="ignore")

    language_code: str = "en-US"
    vocabulary_name: str = "a-vocab"
    filter_name: str = "a-filter"
    filter_method: str = "mask"  # mask (***) | remove | tag (keep text, flag it)
    input_prefix: str = "transcribe/in/"
    output_prefix: str = "transcribe/out/"
    job_prefix: str = "a-"  # IAM policy scopes jobs to transcription-job/a-*
    max_speakers: int = 4  # MaxSpeakerLabels allowed 2..30
    redaction_output: str = "redacted"  # redacted | redacted_and_unredacted
    pii_entity_types: str = "ALL"  # comma list, e.g. "EMAIL,PHONE"; ALL = every supported type
    poll_deadline_s: float = 1800.0
```

- **Catch**: the audio still contains the filtered words

## 3. Language Identification

Language identification (ID) replaces a fixed `LanguageCode` when callers speak different languages.

- `IdentifyLanguage=True`
- Optional `LanguageOptions` narrow the candidates
- Exclusive with `LanguageCode`

```python
# app/infra/_03data_03transcribe.py  (inside start_job)
"LanguageCode": cfg.language_code,  # or IdentifyLanguage=True (+LanguageOptions); exclusive
```

- **Catch**: feature support differs per language
  - Redaction, diarization, streaming
  - Check the supported-languages page

## 4. Output Location And Settings

Writing output to your own bucket keeps transcripts under your encryption and lifecycle.

- `OutputBucketName` + `OutputKey` + a Customer Managed Key (CMK)
  - Otherwise Transcribe uses a service-owned location with a temporary Uniform Resource Locator (URL)
- `OutputKey` ending in `/` means a folder; otherwise a file name
- `MediaFormat` is optional; Transcribe can detect it

```python
# app/infra/_03data_03transcribe.py  (inside start_job)
kwargs: dict[str, Any] = {
    "TranscriptionJobName": name,
    "LanguageCode": cfg.language_code,
    "Media": {"MediaFileUri": media_uri},
    "OutputBucketName": get_settings().data_bucket,
    "OutputKey": f"{cfg.output_prefix}{name}.json",  # a key ending in / means a folder, else a file name
    # OutputEncryptionKMSKeyId="arn:aws:kms:...",  # SSE-KMS for the transcript; caller needs kms perms
    "Settings": settings,
}
ext = media_uri.rsplit(".", 1)[-1].lower()
if ext in _MEDIA_FORMATS:  # mp3, mp4, wav, flac, ogg, amr, webm, m4a
    kwargs["MediaFormat"] = ext  # optional: Transcribe can detect it
```

- **Catch**: the caller needs `s3:PutObject` and a Key Management Service (KMS) data key
  - Else output is unreadable (`AccessDenied`)
