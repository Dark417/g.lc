# modules/04safety_02pii_redaction — Comprehend PII detection/redaction, lectures 26, 49-51 (47 Transcribe, 225 Macie: doc only).
# Creates (all in iam.tf: this component is IAM only): the Comprehend data-access role a-<env>-comprehend-pii (async
#          StartPiiEntitiesDetectionJob reads comprehend/input/ and writes comprehend/output/ in the shared bucket,
#          KMS-encrypted) and the app policy for the sync + async PII APIs and iam:PassRole on that role.
# Used by: python app/{api,service,infra}/_04safety_02pii_redaction (slice "pii").
# Not here: the general NLP Comprehend component (03data_04comprehend) and the guardrail used as the output net
#   (04safety_01guardrails).
#
# Why a service role: async Comprehend jobs run as the Comprehend service, not as the caller. The caller passes
# DataAccessRoleArn, which needs iam:PassRole; the role must trust comprehend.amazonaws.com.
#
# The pipeline (app/service/_04safety_02pii_redaction.redact_converse_guard) also calls bedrock-runtime Converse +
# ApplyGuardrail; those grants come from 04safety_01guardrails (app_guardrails policy) on the same app role.

locals {
  pii_input_prefix  = "comprehend/input/"
  pii_output_prefix = "comprehend/output/"
}
