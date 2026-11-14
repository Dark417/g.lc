variable "prefix" {
  description = "Name prefix <project>-<env>, e.g. a-dev"
  type        = string
}

variable "alert_email" {
  description = "Email that receives cost and GenAI alarms (SNS subscription must be confirmed by hand)"
  type        = string
}

variable "billing_threshold_usd" {
  description = "Alarm when month-to-date estimated charges exceed this many USD"
  type        = number
}
