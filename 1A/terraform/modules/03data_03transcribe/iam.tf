# 03data_03transcribe IAM — app policy (least privilege). No service role for plain jobs.

data "aws_iam_policy_document" "app_transcribe" {
  statement {
    sid     = "Jobs"
    actions = ["transcribe:StartTranscriptionJob", "transcribe:GetTranscriptionJob"]
    resources = [
      "arn:aws:transcribe:${var.region}:${var.account_id}:transcription-job/${var.prefix}-*", # job names start with the prefix
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
  role   = var.app_role_id
  policy = data.aws_iam_policy_document.app_transcribe.json
}
