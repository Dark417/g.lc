# 03.03 transcribe — Amazon Transcribe custom vocabulary + vocabulary filter, lectures 47-48.
# Creates: custom vocabulary a-vocab, vocabulary filter a-filter, app policy for batch jobs.
# Used by: python app/a03_03_transcribe (slice "transcribe").
#
# S3: audio in transcribe/in/, transcripts out transcribe/out/ in the shared bucket (00.05).
# Catch (verify against the Transcribe docs): with OutputBucketName set, Transcribe reads the media and
#   writes the transcript with the CALLER's permissions, so the app role needs s3:GetObject/PutObject
#   (granted bucket-wide in 00.05) and, for SSE-KMS output, kms:GenerateDataKey/Decrypt (granted in 00.03).
#   No separate service role is needed for plain jobs; a DataAccessRole is only for deferred execution.

locals {
  transcribe_language = "en-US" # vocabularies are per language; a job must use the same language
}

resource "aws_transcribe_vocabulary" "main" {
  vocabulary_name = "${local.prefix}-vocab"
  language_code   = local.transcribe_language
  # Phrases: no spaces (use hyphens for multi-word terms), letters only. Takes a minute to become READY.
  phrases = ["Bedrock", "OpenSearch", "Guardrails", "Titan", "Nova-Sonic", "Knowledge-Base"]
  tags    = { Component = "03.03" }
}

resource "aws_transcribe_vocabulary_filter" "main" {
  vocabulary_filter_name = "${local.prefix}-filter"
  language_code          = local.transcribe_language
  words                  = ["darn", "heck"] # applied with VocabularyFilterMethod = mask | remove | tag at job time
  tags                   = { Component = "03.03" }
}

# ---------------------------------------------------------------- app policy (least privilege)

data "aws_iam_policy_document" "app_transcribe" {
  statement {
    sid     = "Jobs"
    actions = ["transcribe:StartTranscriptionJob", "transcribe:GetTranscriptionJob"]
    resources = [
      "arn:aws:transcribe:${var.region}:${local.account_id}:transcription-job/${local.prefix}-*", # job names start with the prefix
    ]
  }
  statement {
    sid       = "ListJobs" # list calls have no resource-level scoping
    actions   = ["transcribe:ListTranscriptionJobs"]
    resources = ["*"]
  }
  statement {
    sid       = "UseVocabulary" # a job that references a vocabulary or filter is authorized against it
    actions   = ["transcribe:GetVocabulary", "transcribe:GetVocabularyFilter"]
    resources = [aws_transcribe_vocabulary.main.arn, aws_transcribe_vocabulary_filter.main.arn]
  }
}

resource "aws_iam_role_policy" "app_transcribe" {
  name   = "transcribe"
  role   = aws_iam_role.app.id
  policy = data.aws_iam_policy_document.app_transcribe.json
}

output "transcribe_vocabulary_name" {
  value = aws_transcribe_vocabulary.main.vocabulary_name
}

output "transcribe_filter_name" {
  value = aws_transcribe_vocabulary_filter.main.vocabulary_filter_name
}
