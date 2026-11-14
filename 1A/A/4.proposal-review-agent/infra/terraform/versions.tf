terraform {
  required_version = ">= 1.6"
  required_providers {
    google      = { source = "hashicorp/google", version = ">= 6.30, < 8" }
    google-beta = { source = "hashicorp/google-beta", version = ">= 6.30, < 8" }
    random      = { source = "hashicorp/random", version = ">= 3.6" }
  }
  # PRODUCTION: remote state.
  # backend "gcs" { bucket = "YOUR-TF-STATE-BUCKET" prefix = "proposal-review" }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}
