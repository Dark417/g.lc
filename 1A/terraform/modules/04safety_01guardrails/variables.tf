variable "prefix" {
  description = "Name prefix <project>-<env>, e.g. a-dev"
  type        = string
}

variable "region" {
  type = string
}

variable "account_id" {
  type = string
}

variable "app_role_id" {
  description = "App role (base_iam) the policy attaches to"
  type        = string
}

variable "kms_key_arn" {
  description = "Shared CMK (base_kms) for the guardrail config at rest"
  type        = string
}

variable "guardrail_tier" {
  description = "CLASSIC or STANDARD. STANDARD = more languages, typo/obfuscation robustness, prompt-leakage detection; needs a cross-Region guardrail profile"
  type        = string

  validation {
    condition     = contains(["CLASSIC", "STANDARD"], var.guardrail_tier)
    error_message = "The guardrail_tier value must be CLASSIC or STANDARD."
  }
}

variable "guardrail_profile_id" {
  description = "System guardrail profile for the STANDARD tier (us.guardrail.v1:0 in us-* Regions)"
  type        = string
}
