# modules/04safety_03evaluations — Amazon Bedrock evaluation jobs (model eval, LLM-as-a-judge, RAG eval), lecture 21 (+190-192).
# Creates: the evaluation service role a-<env>-bedrock-eval (Bedrock assumes it to read datasets, call the generator +
#          judge models and the knowledge base, and write results), the app policy to start/poll/stop jobs (→ iam.tf),
#          and an OPTIONAL example RAG evaluation job (count = 0 by default: jobs are normally started from code).
# Used by: python app/{api,service,infra}/_04safety_03evaluations (slice "evals").
# S3: datasets under evals/datasets/, results under evals/results/ in the shared bucket (base_data_bucket).
# The local guardrail eval harness uses bedrock:ApplyGuardrail, granted by 04safety_01guardrails.
# Cross-component link: var.knowledge_base_id is wired from module._02rag_04knowledge_bases.kb_id in root main.tf
# (it used to be a hand-copied terraform output).

locals {
  eval_dataset_prefix = "evals/datasets/"
  eval_results_prefix = "evals/results/"
  # Generator and judge for the example job. Judge from a different family than the generator reduces
  # self-preference bias; it must be on the supported evaluator list (check the docs).
  eval_generator_model = "anthropic.claude-3-5-haiku-20241022-v1:0" # base-model ARN; newer models may need an inference-profile ARN
  eval_judge_model     = "amazon.nova-pro-v1:0"
}

# ================================================================ optional example: RAG evaluation job as code
# Same request app/infra/_04safety_03evaluations.create_rag_eval sends. Kept behind a flag: a job is an immutable
# one-shot run, so Terraform can create it once but cannot "re-run" it; any change forces a new job.
# Count depends only on the flag (a known value): the KB id comes from another module and is unknown at plan time.

resource "aws_bedrock_evaluation_job" "rag_example" {
  count = var.create_example_job ? 1 : 0

  job_name                   = "${var.prefix}-rag-eval-example"
  job_description            = "Retrieve-and-generate eval of the 02rag_04knowledge_bases knowledge base"
  role_arn                   = aws_iam_role.bedrock_eval.arn
  application_type           = "RagEvaluation" # ModelEvaluation | RagEvaluation
  customer_encryption_key_id = var.kms_key_arn

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
            s3_uri = "s3://${var.data_bucket_name}/${local.eval_dataset_prefix}rag-golden.jsonl"
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
          knowledge_base_id = var.knowledge_base_id
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
    s3_uri = "s3://${var.data_bucket_name}/${local.eval_results_prefix}"
  }

  tags = { Component = "04safety_03evaluations" }
}
