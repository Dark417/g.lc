# Phase 1: everything that doesn't need container images. See docs/design/07-gcp-deployment.md.

data "google_project" "this" {}

locals {
  apis = [
    "run.googleapis.com",
    "sqladmin.googleapis.com",
    "firestore.googleapis.com",
    "storage.googleapis.com",
    "aiplatform.googleapis.com",
    "secretmanager.googleapis.com",
    "artifactregistry.googleapis.com",
    "iap.googleapis.com",
    "compute.googleapis.com",
    "cloudbuild.googleapis.com",
  ]
  registry = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.images.repository_id}"
}

resource "google_project_service" "apis" {
  for_each           = toset(local.apis)
  service            = each.value
  disable_on_destroy = false
}

# ---------------------------------------------------------------- images
resource "google_artifact_registry_repository" "images" {
  repository_id = var.name
  location      = var.region
  format        = "DOCKER"
  depends_on    = [google_project_service.apis]
}

# ---------------------------------------------------------------- network (Direct VPC egress)
resource "google_compute_network" "vpc" {
  name                    = var.name
  auto_create_subnetworks = false
  depends_on              = [google_project_service.apis]
}

resource "google_compute_subnetwork" "run" {
  name                     = "${var.name}-run"
  network                  = google_compute_network.vpc.id
  region                   = var.region
  ip_cidr_range            = "10.20.0.0/24"
  private_ip_google_access = true # lets egress-all services reach *.run.app and Google APIs
}

# ---------------------------------------------------------------- object storage
resource "google_storage_bucket" "docs" {
  name                        = "${var.project_id}-${var.name}"
  location                    = var.region
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"
  versioning { enabled = true }
  lifecycle_rule {
    condition {
      age            = 30
      matches_prefix = ["inbox/"]
    }
    action { type = "Delete" }
  }
}

# ---------------------------------------------------------------- Cloud SQL Postgres + pgvector
resource "random_password" "db" {
  length  = 32
  special = false
}

resource "google_sql_database_instance" "pg" {
  name                = var.name
  database_version    = "POSTGRES_16"
  region              = var.region
  deletion_protection = true
  settings {
    tier              = var.db_tier
    edition           = "ENTERPRISE"
    availability_type = "ZONAL" # PRODUCTION: REGIONAL
    backup_configuration {
      enabled                        = true
      point_in_time_recovery_enabled = true
    }
    ip_configuration { ipv4_enabled = true } # reached only through the Cloud SQL connector socket
    database_flags {
      name  = "cloudsql.iam_authentication"
      value = "on"
    }
  }
  depends_on = [google_project_service.apis]
}

resource "google_sql_database" "app" {
  name     = "compliance"
  instance = google_sql_database_instance.pg.name
}

resource "google_sql_user" "app" {
  name     = "app"
  instance = google_sql_database_instance.pg.name
  password = random_password.db.result
}

# ---------------------------------------------------------------- Firestore with MongoDB compatibility
resource "google_firestore_database" "docs" {
  name             = "${var.name}-docs"
  location_id      = var.firestore_location
  type             = "FIRESTORE_NATIVE"
  database_edition = "ENTERPRISE" # required for the MongoDB-compatible API
  deletion_policy  = "DELETE"
  depends_on       = [google_project_service.apis]
}

# ---------------------------------------------------------------- secrets
resource "random_password" "service_token" {
  length  = 40
  special = false
}

resource "google_secret_manager_secret" "s" {
  for_each  = toset(["database-url", "mongo-url", "service-token"])
  secret_id = "${var.name}-${each.value}"
  replication {
    auto {}
  }
  depends_on = [google_project_service.apis]
}

resource "google_secret_manager_secret_version" "database_url" {
  secret      = google_secret_manager_secret.s["database-url"].id
  secret_data = "postgresql+asyncpg://app:${random_password.db.result}@/compliance?host=/cloudsql/${google_sql_database_instance.pg.connection_name}"
}

resource "google_secret_manager_secret_version" "service_token" {
  secret      = google_secret_manager_secret.s["service-token"].id
  secret_data = random_password.service_token.result
}

resource "google_secret_manager_secret_version" "mongo_url" {
  count       = var.mongo_url == "" ? 0 : 1
  secret      = google_secret_manager_secret.s["mongo-url"].id
  secret_data = var.mongo_url
}

# ---------------------------------------------------------------- service accounts (least privilege)
resource "google_service_account" "sa" {
  for_each     = toset(["backend", "frontend", "mcp"])
  account_id   = "${var.name}-${each.value}"
  display_name = "${var.name} ${each.value}"
}

resource "google_project_iam_member" "backend" {
  for_each = toset(["roles/aiplatform.user", "roles/cloudsql.client", "roles/datastore.user"])
  project  = var.project_id
  role     = each.value
  member   = google_service_account.sa["backend"].member
}

resource "google_storage_bucket_iam_member" "backend" {
  bucket = google_storage_bucket.docs.name
  role   = "roles/storage.objectAdmin"
  member = google_service_account.sa["backend"].member
}

resource "google_secret_manager_secret_iam_member" "backend" {
  for_each  = toset(["database-url", "mongo-url", "service-token"])
  secret_id = google_secret_manager_secret.s[each.value].id
  role      = "roles/secretmanager.secretAccessor"
  member    = google_service_account.sa["backend"].member
}

resource "google_secret_manager_secret_iam_member" "mcp" {
  secret_id = google_secret_manager_secret.s["service-token"].id
  role      = "roles/secretmanager.secretAccessor"
  member    = google_service_account.sa["mcp"].member
}

# ---------------------------------------------------------------- IAP (who may open the portal)
resource "google_project_service_identity" "iap" {
  provider = google-beta
  service  = "iap.googleapis.com"
}

resource "google_iap_web_iam_member" "people" {
  for_each = toset(concat([for e in var.admin_emails : "user:${e}"], [for e in var.user_emails : (strcontains(e, ":") ? e : "user:${e}")]))
  role     = "roles/iap.httpsResourceAccessor"
  member   = each.value
}
