# modules/03data_04comprehend — Amazon Comprehend + Comprehend Medical, lectures 49-52.
# Creates: only the app policy (→ iam.tf). Comprehend is pay-per-call, so there is nothing to provision.
# Used by: python app/{api,service,infra}/_03data_04comprehend (slice "comprehend").
# PII APIs (comprehend:DetectPiiEntities, ContainsPiiEntities) are granted by 04safety_02pii_redaction, not here.
#
# Not declared on purpose: custom models. Training + an inference endpoint bill per hour even when idle.
# Example (commented, never applied):
#
# resource "aws_comprehend_document_classifier" "tickets" {
#   name                  = "${var.prefix}-tickets"
#   language_code         = "en"
#   mode                  = "MULTI_CLASS"       # or MULTI_LABEL
#   data_access_role_arn  = aws_iam_role.comprehend_data.arn # trust comprehend.amazonaws.com, read s3 comprehend/train/
#   model_kms_key_id      = var.kms_key_arn
#   volume_kms_key_id     = var.kms_key_arn
#   input_data_config {
#     s3_uri      = "s3://${var.data_bucket_name}/comprehend/train/tickets.csv" # label,text per line
#     data_format = "COMPREHEND_CSV"
#   }
# }
# Real-time use then needs an endpoint (created with the CreateEndpoint API), billed per inference
# unit-hour: delete it when idle.
