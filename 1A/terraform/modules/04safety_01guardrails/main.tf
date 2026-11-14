# modules/04safety_01guardrails — Amazon Bedrock Guardrails, lectures 23-25 (guardrails, automated reasoning, hands-on), 34.
# Creates: guardrail a-<env>-guardrail with EVERY policy type the Terraform schema supports (content filters incl.
#          prompt attack, denied topics, word filters, sensitive information PII + regex, contextual grounding,
#          tier + cross-Region profile, KMS), one immutable version, and the app IAM policy (→ iam.tf).
# Used by: python app/{api,service,infra}/_04safety_01guardrails (slice "guardrails"),
#          java com.lc.a.{api,service,infra}._04safety_01guardrails (a.guardrails.*),
#          and as the output guard in app/service/_04safety_02pii_redaction.
#
# Same policy in code: app/infra/_04safety_01guardrails.py builds the identical request with one builder function per
# policy (content_policy, topic_policy, ...). Terraform owns THIS resource; the SDK path is for tooling/tests.
#
# Not in the provider 6.73 schema (SDK only, see app/infra/_04safety_01guardrails.py):
#   - automatedReasoningPolicyConfig (Automated Reasoning checks, lecture 24)
#   - contextual grounding tierConfig, denied-topic inputAction/outputAction (detect mode for topics)
#
# Versions: aws_bedrock_guardrail = the mutable DRAFT. aws_bedrock_guardrail_version = an immutable snapshot of
#   DRAFT at create time. Changing the guardrail does NOT re-snapshot: add "v2" (or -replace) to publish.

locals {
  guardrail_name = "${var.prefix}-guardrail"

  # System-defined guardrail profile for cross-Region processing (STANDARD tier). Geography prefix must match the
  # Region: us.* for us-*, eu.* for eu-*, apac.* for ap-* (verify the exact id in the console / ListGuardrails).
  guardrail_profile_id = var.guardrail_profile_id

  # Content filter categories -> [input strength, output strength].
  # Strength = the lowest classifier confidence that blocks: HIGH blocks LOW+MEDIUM+HIGH (most recall, most false
  # positives), LOW blocks only HIGH-confidence hits, NONE = off. Tune from the labeled eval set (04safety_03evaluations).
  content_filters = {
    HATE       = ["HIGH", "HIGH"]
    INSULTS    = ["MEDIUM", "MEDIUM"] # example of a lowered category: casual support chats contain mild insults
    SEXUAL     = ["HIGH", "HIGH"]
    VIOLENCE   = ["MEDIUM", "HIGH"] # users describe incidents ("my car was hit") -> lower on input
    MISCONDUCT = ["HIGH", "HIGH"]   # criminal activity, self-harm facilitation
  }
}

# ================================================================ guardrail (DRAFT)

resource "aws_bedrock_guardrail" "main" {
  name        = local.guardrail_name
  description = "1A demo guardrail: every policy type, configured as code"

  # Shown instead of the model call (input) or the model answer (output) when a BLOCK policy hits.
  # Tell the user what to do next; never echo what was detected.
  blocked_input_messaging   = "Sorry, I can't help with that request. Please rephrase or contact support."
  blocked_outputs_messaging = "Sorry, I can't share that answer. Please contact support for help."

  # CMK for the guardrail config at rest. Callers need kms:Decrypt on it (granted in base_iam).
  kms_key_arn = var.kms_key_arn

  # ---------------------------------------------------------------- content filters (+ prompt attack)
  content_policy_config {
    dynamic "filters_config" {
      for_each = local.content_filters
      content {
        type              = filters_config.key
        input_strength    = filters_config.value[0]
        output_strength   = filters_config.value[1]
        input_modalities  = ["TEXT", "IMAGE"] # IMAGE: also classify png/jpeg content blocks (extra image units)
        output_modalities = ["TEXT"]
        input_action      = "BLOCK" # NONE = detect mode: evaluate + report (detected=true) but do not block
        output_action     = "BLOCK"
        input_enabled     = true
        output_enabled    = true
      }
    }

    # Prompt attack = jailbreak + prompt injection (+ prompt leakage on STANDARD). Input only:
    # output_strength MUST be NONE or the API rejects the guardrail.
    # Catch: it scans every untagged message incl. your system prompt -> tag user text with guardContent.
    filters_config {
      type             = "PROMPT_ATTACK"
      input_strength   = "HIGH"
      output_strength  = "NONE"
      input_modalities = ["TEXT"]
      input_action     = "BLOCK"
      input_enabled    = true
    }

    # CLASSIC | STANDARD per policy. STANDARD needs cross_region_config below.
    tier_config = [{ tier_name = var.guardrail_tier }]
  }

  # ---------------------------------------------------------------- denied topics
  topic_policy_config {
    # Definition = describe the topic (not "don't do X"). Examples = up to 5 typical user phrasings.
    # The classifier is semantic: it also catches paraphrases, and near misses -> check FP on the eval set.
    topics_config {
      name       = "InvestmentAdvice"
      type       = "DENY" # only value
      definition = "Personalized recommendations about buying, selling, or allocating stocks, bonds, funds, crypto, or other financial assets."
      examples = [
        "Which stocks should I buy this month?",
        "Should I move my 401k into crypto?",
        "Is now a good time to sell my Tesla shares?",
      ]
    }

    topics_config {
      name       = "LegalAdvice"
      type       = "DENY"
      definition = "Guidance on how to handle a specific legal dispute, lawsuit, contract breach, or criminal charge."
      examples = [
        "How do I sue my landlord?",
        "What should I say to the police about the accident?",
      ]
    }

    tier_config = [{ tier_name = var.guardrail_tier }]
  }

  # ---------------------------------------------------------------- word filters
  word_policy_config {
    # Exact (case-insensitive) words/phrases: cheap and precise. Good for code names and competitor names.
    words_config {
      text           = "Project Nightingale" # internal code name must never leak in answers
      input_action   = "NONE"                # users may type it; detect only on input
      output_action  = "BLOCK"
      input_enabled  = true
      output_enabled = true
    }
    words_config {
      text = "CompetitorCo"
    }

    # AWS-managed profanity list (only managed list type today).
    managed_word_lists_config {
      type = "PROFANITY"
    }
  }

  # ---------------------------------------------------------------- sensitive information (PII + regex)
  sensitive_information_policy_config {
    # ANONYMIZE: replaced by {EMAIL} / {PHONE}; the call continues. Input anonymize = model never sees it.
    pii_entities_config {
      type   = "EMAIL"
      action = "ANONYMIZE"
    }
    pii_entities_config {
      type   = "PHONE"
      action = "ANONYMIZE"
    }
    # Asymmetric: let users give their name (detect only on input), mask names the model emits.
    pii_entities_config {
      type          = "NAME"
      action        = "ANONYMIZE"
      input_action  = "NONE"
      output_action = "ANONYMIZE"
    }
    # BLOCK: identifiers that must never flow in either direction refuse the whole call.
    pii_entities_config {
      type   = "US_SOCIAL_SECURITY_NUMBER"
      action = "BLOCK"
    }
    pii_entities_config {
      type   = "CREDIT_DEBIT_CARD_NUMBER"
      action = "BLOCK"
    }
    pii_entities_config {
      type   = "AWS_SECRET_KEY"
      action = "BLOCK"
    }

    # Custom regex for ids the built-in detector does not know. Masked as {InternalAccountId}.
    # Keep patterns anchored and non-greedy: they run on every request.
    regexes_config {
      name        = "InternalAccountId"
      description = "Internal account id, e.g. ACCT-12345678"
      pattern     = "ACCT-[0-9]{8}"
      action      = "ANONYMIZE"
    }
  }

  # ---------------------------------------------------------------- contextual grounding (RAG answers)
  # Needs grounding_source + query + guard_content qualifiers at call time; otherwise it is skipped.
  # Block when score < threshold (0 to 0.99). Higher = stricter = more refusals of partly supported answers.
  contextual_grounding_policy_config {
    filters_config {
      type      = "GROUNDING" # is the answer supported by the source passages?
      threshold = 0.75
    }
    filters_config {
      type      = "RELEVANCE" # does the answer address the query?
      threshold = 0.5
    }
  }

  # ---------------------------------------------------------------- cross-Region profile (STANDARD tier)
  # Guardrail inference may run in another Region of the same geography (data residency review!).
  dynamic "cross_region_config" {
    for_each = var.guardrail_tier == "STANDARD" ? [1] : []
    content {
      guardrail_profile_identifier = local.guardrail_profile_id
    }
  }

  tags = { Component = "04safety_01guardrails" }
}

# ================================================================ immutable version

resource "aws_bedrock_guardrail_version" "v1" {
  guardrail_arn = aws_bedrock_guardrail.main.guardrail_arn
  description   = "v1: initial policy set"
  skip_destroy  = true # keep old versions when this resource is replaced, so apps pinned to "1" keep working
}
