variable "project_id" {
  type = string
}

variable "region" {
  type    = string
  default = "us-central1"
}

variable "name" {
  description = "Prefix for resource names."
  type        = string
  default     = "proposal-review"
}

variable "admin_emails" {
  description = "Admins in the app (ADMIN_USERS) and allowed through IAP."
  type        = list(string)
}

variable "user_emails" {
  description = "Other people allowed through IAP (role: user). Use group:... members for real teams."
  type        = list(string)
  default     = []
}

variable "mcp_invokers" {
  description = "IAM members allowed to call the MCP server, e.g. [\"user:you@company.com\"]."
  type        = list(string)
  default     = []
}

# --- two-phase apply (see docs/DEPLOY.md) ---
variable "deploy_services" {
  description = "false: foundation only (APIs, DB, bucket, registry...). true: also Cloud Run services + job. Needs images pushed and mongo_url set."
  type        = bool
  default     = false
}

variable "image_tag" {
  description = "Initial image tag for Cloud Run. CI moves tags afterwards (Terraform ignores image changes)."
  type        = string
  default     = "latest"
}

variable "mongo_url" {
  description = "Firestore (MongoDB compatibility) connection string, created after phase 1. See docs/DEPLOY.md."
  type        = string
  default     = ""
  sensitive   = true
}

# --- sizing / model ---
variable "db_tier" {
  type    = string
  default = "db-custom-1-3840"
}

variable "model" {
  type    = string
  default = "gemini-2.5-flash"
}

variable "vertex_location" {
  type    = string
  default = "us-central1"
}

variable "firestore_location" {
  description = "Firestore location; nam5 / eur3 are multi-region, or use a region."
  type        = string
  default     = "nam5"
}
