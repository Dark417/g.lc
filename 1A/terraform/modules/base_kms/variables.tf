variable "prefix" {
  description = "Name prefix <project>-<env>, e.g. a-dev"
  type        = string
}

variable "deletion_window_in_days" {
  description = "Waiting period before a deleted key is gone for good (7-30)"
  type        = number
}
