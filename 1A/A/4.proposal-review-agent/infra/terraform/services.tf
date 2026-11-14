# Phase 2 (deploy_services = true): Cloud Run services + ingest job. Images must exist in Artifact
# Registry first (cloudbuild.yaml), and mongo_url must be set.

locals {
  n = var.deploy_services ? 1 : 0

  backend_env = {
    GOOGLE_GENAI_USE_VERTEXAI = "TRUE"
    GOOGLE_CLOUD_PROJECT      = var.project_id
    GOOGLE_CLOUD_LOCATION     = var.vertex_location
    MODEL                     = var.model
    EMBEDDER                  = "gemini"
    VECTOR_STORE              = "pgvector"
    DOC_STORE                 = "mongo"
    MONGO_DB                  = google_firestore_database.docs.name
    BLOB_STORE                = "gcs"
    GCS_BUCKET                = google_storage_bucket.docs.name
    MEMORY_BACKEND            = "sql"
    AUTH_MODE                 = "iap"
    # Cloud Run's built-in IAP audience. Verify in IAP console -> service -> "Get JWT audience".
    IAP_AUDIENCE   = "/projects/${data.google_project.this.number}/locations/${var.region}/services/frontend"
    ADMIN_USERS    = join(",", var.admin_emails)
    ENABLE_ADK_WEB = "false" # the dev UI has no auth
    LOG_LEVEL      = "INFO"
  }
  backend_secrets = {
    DATABASE_URL   = "database-url"
    MONGO_URL      = "mongo-url"
    SERVICE_TOKENS = "service-token"
  }
}

# ---------------------------------------------------------------- backend (internal only)
resource "google_cloud_run_v2_service" "backend" {
  count               = local.n
  name                = "backend"
  location            = var.region
  ingress             = "INGRESS_TRAFFIC_INTERNAL_ONLY"
  deletion_protection = false

  template {
    service_account = google_service_account.sa["backend"].email
    timeout         = "300s" # SSE chat streams
    scaling {
      min_instance_count = 0
      max_instance_count = 5
    }
    volumes {
      name = "cloudsql"
      cloud_sql_instance { instances = [google_sql_database_instance.pg.connection_name] }
    }
    containers {
      image = "${local.registry}/backend:${var.image_tag}"
      ports { container_port = 8000 }
      resources {
        limits = { cpu = "1", memory = "1Gi" }
      }
      dynamic "env" {
        for_each = local.backend_env
        content {
          name  = env.key
          value = env.value
        }
      }
      dynamic "env" {
        for_each = local.backend_secrets
        content {
          name = env.key
          value_source {
            secret_key_ref {
              secret  = google_secret_manager_secret.s[env.value].secret_id
              version = "latest"
            }
          }
        }
      }
      volume_mounts {
        name       = "cloudsql"
        mount_path = "/cloudsql"
      }
      startup_probe {
        http_get { path = "/readyz" }
        period_seconds    = 5
        failure_threshold = 24
      }
    }
  }
  lifecycle { ignore_changes = [template[0].containers[0].image, client, client_version] }
  depends_on = [google_secret_manager_secret_version.mongo_url, google_project_iam_member.backend]
}

# Ingress is internal-only, so only the VPC-egress services (frontend, mcp) can reach it.
# The backend still authenticates every request itself (IAP JWT or service token).
resource "google_cloud_run_v2_service_iam_member" "backend_invoker" {
  count    = local.n
  name     = google_cloud_run_v2_service.backend[0].name
  location = var.region
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# ---------------------------------------------------------------- frontend (public, behind IAP)
resource "google_cloud_run_v2_service" "frontend" {
  count               = local.n
  provider            = google-beta
  name                = "frontend"
  location            = var.region
  ingress             = "INGRESS_TRAFFIC_ALL"
  launch_stage        = "BETA"
  iap_enabled         = true
  deletion_protection = false

  template {
    service_account = google_service_account.sa["frontend"].email
    timeout         = "300s"
    vpc_access {
      egress = "ALL_TRAFFIC" # so calls to the internal backend count as internal
      network_interfaces {
        network    = google_compute_network.vpc.id
        subnetwork = google_compute_subnetwork.run.id
      }
    }
    containers {
      image = "${local.registry}/frontend:${var.image_tag}"
      ports { container_port = 8080 }
      env {
        name  = "BACKEND_URL"
        value = google_cloud_run_v2_service.backend[0].uri
      }
      resources {
        limits = { cpu = "1", memory = "256Mi" }
      }
    }
  }
  lifecycle { ignore_changes = [template[0].containers[0].image, client, client_version] }
}

resource "google_cloud_run_v2_service_iam_member" "iap_invokes_frontend" {
  count    = local.n
  name     = google_cloud_run_v2_service.frontend[0].name
  location = var.region
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_project_service_identity.iap.email}"
}

# ---------------------------------------------------------------- MCP server (IAM-authenticated)
resource "google_cloud_run_v2_service" "mcp" {
  count               = local.n
  name                = "mcp-server"
  location            = var.region
  ingress             = "INGRESS_TRAFFIC_ALL"
  deletion_protection = false

  template {
    service_account = google_service_account.sa["mcp"].email
    vpc_access {
      egress = "ALL_TRAFFIC"
      network_interfaces {
        network    = google_compute_network.vpc.id
        subnetwork = google_compute_subnetwork.run.id
      }
    }
    containers {
      image = "${local.registry}/mcp-server:${var.image_tag}"
      ports { container_port = 8001 }
      env {
        name  = "BACKEND_URL"
        value = google_cloud_run_v2_service.backend[0].uri
      }
      env {
        name = "SERVICE_TOKEN"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.s["service-token"].secret_id
            version = "latest"
          }
        }
      }
    }
  }
  lifecycle { ignore_changes = [template[0].containers[0].image, client, client_version] }
}

resource "google_cloud_run_v2_service_iam_member" "mcp_invokers" {
  for_each = var.deploy_services ? toset(var.mcp_invokers) : toset([])
  name     = google_cloud_run_v2_service.mcp[0].name
  location = var.region
  role     = "roles/run.invoker"
  member   = each.value
}

# ---------------------------------------------------------------- bulk ingest job (same image)
resource "google_cloud_run_v2_job" "ingest" {
  count               = local.n
  name                = "ingest"
  location            = var.region
  deletion_protection = false

  template {
    task_count = 1
    template {
      service_account = google_service_account.sa["backend"].email
      timeout         = "3600s"
      max_retries     = 1
      volumes {
        name = "cloudsql"
        cloud_sql_instance { instances = [google_sql_database_instance.pg.connection_name] }
      }
      containers {
        image   = "${local.registry}/backend:${var.image_tag}"
        command = ["python", "-m", "app.cli", "ingest", "gs://${google_storage_bucket.docs.name}/inbox"]
        resources {
          limits = { cpu = "2", memory = "2Gi" }
        }
        dynamic "env" {
          for_each = local.backend_env
          content {
            name  = env.key
            value = env.value
          }
        }
        dynamic "env" {
          for_each = local.backend_secrets
          content {
            name = env.key
            value_source {
              secret_key_ref {
                secret  = google_secret_manager_secret.s[env.value].secret_id
                version = "latest"
              }
            }
          }
        }
        volume_mounts {
          name       = "cloudsql"
          mount_path = "/cloudsql"
        }
      }
    }
  }
  lifecycle { ignore_changes = [template[0].template[0].containers[0].image, client, client_version] }
}
