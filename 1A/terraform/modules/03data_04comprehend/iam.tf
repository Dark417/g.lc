# 03data_04comprehend IAM — app policy for the Detect*, ClassifyDocument and Comprehend Medical APIs.

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
    resources = ["arn:aws:comprehend:${var.region}:${var.account_id}:document-classifier-endpoint/*"]
  }
  statement {
    sid       = "Medical"
    actions   = ["comprehendmedical:DetectEntitiesV2", "comprehendmedical:DetectPHI", "comprehendmedical:InferICD10CM"]
    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "app_comprehend" {
  name   = "comprehend"
  role   = var.app_role_id
  policy = data.aws_iam_policy_document.app_comprehend.json
}
