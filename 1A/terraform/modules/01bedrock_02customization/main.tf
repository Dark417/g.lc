# modules/01bedrock_02customization — the service role a customization job runs as, and the app permissions to
# start jobs, read results, and (deliberately, by hand) buy provisioned throughput to serve the result.
#
# Creates (all in iam.tf: this component is IAM only)
#   - aws_iam_role.customization "a-<env>-customization-role" (assumed by bedrock.amazonaws.com during training)
#   - aws_iam_role_policy.customization on the app role (base_iam)
# Does NOT create (they train or bill by the hour): aws_bedrock_custom_model, aws_bedrock_provisioned_model_throughput.
#   Commented examples are at the bottom. The Python slice shows the same calls with explicit warnings.
# Data: shared bucket a-<env>-ai-data-<account> (base_data_bucket), prefixes customization/train/,
#   customization/validation/, customization/output/.
# Used by: Python app/{api,service,infra}/_01bedrock_02customization
# Lectures: AIP-C01 #11–#12

locals {
  customization_prefix = "customization"
  customization_base   = "arn:aws:bedrock:${var.region}::foundation-model/${var.customization_base_model_id}"
}

# ---------------------------------------------------------------- commented examples (NOT live resources)

# Training job as a Terraform resource: `apply` would start a paid, hours-long training run, and a later
# change to any argument replaces (re-trains) the model. Kept as a reference for the argument names (6.73).
#
# resource "aws_bedrock_custom_model" "summary" {
#   custom_model_name     = "${var.prefix}-summary-model"
#   job_name              = "${var.prefix}-summary-job-1"
#   base_model_identifier = local.customization_base
#   role_arn              = aws_iam_role.customization.arn
#   customization_type    = "FINE_TUNING"          # FINE_TUNING | CONTINUED_PRE_TRAINING | DISTILLATION
#   custom_model_kms_key_id = var.kms_key_arn
#   hyperparameters = {                              # string map; names and ranges are per base model
#     epochCount   = "2"
#     batchSize    = "1"
#     learningRate = "0.00001"
#   }
#   training_data_config   { s3_uri = "s3://${var.data_bucket_name}/customization/train/train.jsonl" }
#   validation_data_config { validator { s3_uri = "s3://${var.data_bucket_name}/customization/validation/validation.jsonl" } }
#   output_data_config     { s3_uri = "s3://${var.data_bucket_name}/customization/output/" }
# }
#
# Provisioned throughput: bills per model unit per hour from creation until deletion.
# resource "aws_bedrock_provisioned_model_throughput" "summary" {
#   provisioned_model_name = "${var.prefix}-summary-pt"
#   model_arn              = aws_bedrock_custom_model.summary.custom_model_arn
#   model_units            = 1
#   # commitment_duration  = "OneMonth"   # OneMonth | SixMonths; omit = no commitment (hourly, deletable)
# }
