# 04.03 evaluations — Amazon Bedrock evaluation jobs (model eval, LLM-as-a-judge, RAG eval), lecture 21 (+190-192).
# Creates: the evaluation service role a-bedrock-eval (Bedrock assumes it to read datasets, call the generator +
#          judge models and the knowledge base, and write results), the app policy to start/poll/stop jobs, and an
#          OPTIONAL example RAG evaluation job (count = 0 by default: jobs are normally started from code).
# Used by: python app/a04_03_evaluations (slice "evals").
# S3: datasets under evals/datasets/, results under evals/results/ in the shared bucket (00.05).
# The local guardrail eval harness uses bedrock:ApplyGuardrail, granted by 04.01.

variable "eval_knowledge_base_id" {
  description = "Knowledge base id for the example RAG eval job (terraform output of 02.04); empty = no example job"
  type        = string
  default     = ""
}

variable "eval_create_example_job" {
  description = "Create the example RAG evaluation job. A job is a one-shot run: re-applying does not re-run it"
  type        = bool
  default     = false
}

locals {
  eval_dataset_prefix = "evals/datasets/"
  eval_results_prefix = "evals/results/"
  # Generator and judge for the example job. Judge from a different family than the generator reduces
  # self-preference bias; it must be on the supported evaluator list (check the docs).
  eval_generator_model = "anthropic.claude-3-5-haiku-20241022-v1:0" # base-model ARN; newer models may need an inference-profile ARN
  eval_judge_model     = "amazon.nova-pro-v1:0"
}

# ================================================================ evaluation service role

data "aws_iam_policy_document" "bedrock_eval_trust" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["bedrock.amazonaws.com"]
    }
    # Confused-deputy guard: only evaluation jobs in this account may assume the role.
    condition {
      test     = "StringEquals"
      variable = "aws:SourceAccount"
      values   = [local.account_id]
    }
    condition {
      test     = "ArnLike"
      variable = "aws:SourceArn"
      values   = ["arn:aws:bedrock:${var.region}:${local.account_id}:evaluation-job/*"]
    }
  }
}

resource "aws_iam_role" "bedrock_eval" {
  name               = "${local.prefix}-bedrock-eval"
  assume_role_policy = data.aws_iam_policy_document.bedrock_eval_trust.json
  tags               = { Component = "04.03" }
}

data "aws_iam_policy_document" "bedrock_eval_access" {
  statement {
    sid       = "ListEvalPrefixes"
    actions   = ["s3:ListBucket"]
    resources = [aws_s3_bucket.data.arn]
    condition {
      test     = "StringLike"
      variable = "s3:prefix"
      values   = ["${local.eval_dataset_prefix}*", "${local.eval_results_prefix}*"]
    }
  }
  statement {
    sid       = "ReadDatasets"
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.data.arn}/${local.eval_dataset_prefix}*"]
  }
  statement {
    sid       = "WriteResults"
    actions   = ["s3:PutObject", "s3:GetObject"] # GetObject: the job re-reads partial results it wrote
    resources = ["${aws_s3_bucket.data.arn}/${local.eval_results_prefix}*"]
  }

  # Generator + judge inference. Cross-Region inference profiles fan out to several Regions -> Region "*".
  statement {
    sid     = "InvokeGeneratorAndJudge"
    actions = ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream", "bedrock:GetInferenceProfile"]
    resources = [
      "arn:aws:bedrock:*::foundation-model/*",
      "arn:aws:bedrock:*:${local.account_id}:inference-profile/*",
    ]
  }

  # RAG evaluation: the job calls the knowledge base itself (retrieve-only or retrieve-and-generate).
  statement {
    sid       = "QueryKnowledgeBases"
    actions   = ["bedrock:Retrieve", "bedrock:RetrieveAndGenerate"]
    resources = ["arn:aws:bedrock:${var.region}:${local.account_id}:knowledge-base/*"]
  }

  # Datasets are SSE-KMS (bucket default) and results are written with customerEncryptionKeyId = the same CMK.
  statement {
    sid       = "UseDataKey"
    actions   = ["kms:Decrypt", "kms:GenerateDataKey", "kms:DescribeKey"]
    resources = [aws_kms_key.main.arn]
  }
}

resource "aws_iam_role_policy" "bedrock_eval_access" {
  name   = "s3-models-kb-kms"
  role   = aws_iam_role.bedrock_eval.id
  policy = data.aws_iam_policy_document.bedrock_eval_access.json
}

# ================================================================ app IAM (least privilege)

data "aws_iam_policy_document" "app_evals" {
  statement {
    sid = "EvaluationJobs"
    actions = [
      "bedrock:CreateEvaluationJob",
      "bedrock:GetEvaluationJob",
      "bedrock:StopEvaluationJob",
    ]
    resources = ["arn:aws:bedrock:${var.region}:${local.account_id}:evaluation-job/*"]
  }

  # List APIs cannot be scoped to a resource ARN.
  statement {
    sid       = "ListJobs"
    actions   = ["bedrock:ListEvaluationJobs"]
    resources = ["*"]
  }

  statement {
    sid       = "PassEvalRole"
    actions   = ["iam:PassRole"]
    resources = [aws_iam_role.bedrock_eval.arn]
    condition {
      test     = "StringEquals"
      variable = "iam:PassedToService"
      values   = ["bedrock.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy" "app_evals" {
  name   = "evaluations"
  role   = aws_iam_role.app.id
  policy = data.aws_iam_policy_document.app_evals.json
}

# ================================================================ optional example: RAG evaluation job as code
# Same request infra.create_rag_eval sends. Kept behind a flag: a job is an immutable one-shot run, so Terraform
# can create it once but cannot "re-run" it; any change forces a new job.

resource "aws_bedrock_evaluation_job" "rag_example" {
  count = var.eval_create_example_job && var.eval_knowledge_base_id != "" ? 1 : 0

  job_name                   = "${local.prefix}-rag-eval-example"
  job_description            = "Retrieve-and-generate eval of the 02.04 knowledge base"
  role_arn                   = aws_iam_role.bedrock_eval.arn
  application_type           = "RagEvaluation" # ModelEvaluation | RagEvaluation
  customer_encryption_key_id = aws_kms_key.main.arn

  evaluation_config {
    automated {
      dataset_metric_config {
        task_type = "QuestionAndAnswer" # ignored for RAG jobs, still required by the schema
        metric_names = [
          "Builtin.Correctness",
          "Builtin.Completeness",
          "Builtin.Faithfulness",
          "Builtin.Helpfulness",
        ]
        dataset {
          name = "rag-golden"
          dataset_location {
            s3_uri = "s3://${aws_s3_bucket.data.bucket}/${local.eval_dataset_prefix}rag-golden.jsonl"
          }
        }
      }
      evaluator_model_config {
        bedrock_evaluator_model {
          model_identifier = local.eval_judge_model
        }
      }
    }
  }

  inference_config {
    rag_config {
      knowledge_base_config {
        retrieve_and_generate_config {
          knowledge_base_id = var.eval_knowledge_base_id
          model_arn         = "arn:aws:bedrock:${var.region}::foundation-model/${local.eval_generator_model}"
          retrieval_configuration {
            vector_search_configuration {
              number_of_results = 5 # top-k; raise when ContextCoverage is low
            }
          }
        }
      }
    }
  }

  output_data_config {
    s3_uri = "s3://${aws_s3_bucket.data.bucket}/${local.eval_results_prefix}"
  }

  tags = { Component = "04.03" }
}

# ================================================================ outputs

output "bedrock_eval_role_arn" {
  value = aws_iam_role.bedrock_eval.arn # A_EVALS_ROLE_ARN
}

output "eval_datasets_s3_uri" {
  value = "s3://${aws_s3_bucket.data.bucket}/${local.eval_dataset_prefix}"
}

output "eval_results_s3_uri" {
  value = "s3://${aws_s3_bucket.data.bucket}/${local.eval_results_prefix}"
}
