# 03.04 comprehend — Amazon Comprehend + Comprehend Medical, lectures 49-52.
# Creates: only the app policy. Comprehend is pay-per-call, so there is nothing to provision.
# Used by: python app/a03_04_comprehend (slice "comprehend").
# PII APIs (comprehend:DetectPiiEntities, ContainsPiiEntities) are granted by 04.02, not here.
#
# Not declared on purpose: custom models. Training + an inference endpoint bill per hour even when idle.
# Example (commented, never applied):
#
# resource "aws_comprehend_document_classifier" "tickets" {
#   name                  = "${local.prefix}-tickets"
#   language_code         = "en"
#   mode                  = "MULTI_CLASS"       # or MULTI_LABEL
#   data_access_role_arn  = aws_iam_role.comprehend_data.arn # trust comprehend.amazonaws.com, read s3 comprehend/train/
#   model_kms_key_id      = aws_kms_key.main.arn
#   volume_kms_key_id     = aws_kms_key.main.arn
#   input_data_config {
#     s3_uri      = "s3://${aws_s3_bucket.data.bucket}/comprehend/train/tickets.csv" # label,text per line
#     data_format = "COMPREHEND_CSV"
#   }
# }
# Real-time use then needs an endpoint (created with the CreateEndpoint API), billed per inference
# unit-hour: delete it when idle.

data "aws_iam_policy_document" "app_comprehend" {
  statement {
    sid = "Detect"
    actions = [
      "comprehend:DetectEntities", "comprehend:DetectKeyPhrases", "comprehend:DetectSentiment",
      "comprehend:DetectTargetedSentiment", "comprehend:DetectDominantLanguage", "comprehend:DetectSyntax",
      "comprehend:BatchDetectEntities", "comprehend:BatchDetectKeyPhrases", "comprehend:BatchDetectSentiment",
      "comprehend:BatchDetectTargetedSentiment", "comprehend:BatchDetectDominantLanguage", "comprehend:BatchDetectSyntax",
    ]
    resources = ["*"] # the Detect* APIs have no resource-level scoping
  }
  statement {
    sid       = "Classify" # custom classifier endpoints only; scoped to this account's endpoints
    actions   = ["comprehend:ClassifyDocument"]
    resources = ["arn:aws:comprehend:${var.region}:${local.account_id}:document-classifier-endpoint/*"]
  }
  statement {
    sid       = "Medical"
    actions   = ["comprehendmedical:DetectEntitiesV2", "comprehendmedical:DetectPHI", "comprehendmedical:InferICD10CM"]
    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "app_comprehend" {
  name   = "comprehend"
  role   = aws_iam_role.app.id
  policy = data.aws_iam_policy_document.app_comprehend.json
}
