variable "prefix" {
  description = "Name prefix <project>-<env>, e.g. a-dev"
  type        = string
}

variable "kms_key_arn" {
  description = "Shared CMK (base_kms) the app encrypts / decrypts with"
  type        = string
}
