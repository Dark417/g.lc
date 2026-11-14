# modules/03data_03transcribe — Amazon Transcribe custom vocabulary + vocabulary filter, lectures 47-48.
# Creates: custom vocabulary a-<env>-vocab, vocabulary filter a-<env>-filter, app policy for batch jobs (→ iam.tf).
# Used by: python app/{api,service,infra}/_03data_03transcribe (slice "transcribe").
#
# S3: audio in transcribe/in/, transcripts out transcribe/out/ in the shared bucket (base_data_bucket).
# Catch (verify against the Transcribe docs): with OutputBucketName set, Transcribe reads the media and
#   writes the transcript with the CALLER's permissions, so the app role needs s3:GetObject/PutObject
#   (granted bucket-wide in base_data_bucket) and, for SSE-KMS output, kms:GenerateDataKey/Decrypt
#   (granted in base_iam).
#   No separate service role is needed for plain jobs; a DataAccessRole is only for deferred execution.

locals {
  transcribe_language = "en-US" # vocabularies are per language; a job must use the same language
}

resource "aws_transcribe_vocabulary" "main" {
  vocabulary_name = "${var.prefix}-vocab"
  language_code   = local.transcribe_language
  # Phrases: no spaces (use hyphens for multi-word terms), letters only. Takes a minute to become READY.
  phrases = ["Bedrock", "OpenSearch", "Guardrails", "Titan", "Nova-Sonic", "Knowledge-Base"]
  tags    = { Component = "03data_03transcribe" }
}

resource "aws_transcribe_vocabulary_filter" "main" {
  vocabulary_filter_name = "${var.prefix}-filter"
  language_code          = local.transcribe_language
  words                  = ["darn", "heck"] # applied with VocabularyFilterMethod = mask | remove | tag at job time
  tags                   = { Component = "03data_03transcribe" }
}
