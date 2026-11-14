output "registry" {
  value = local.registry
}

output "bucket" {
  value = google_storage_bucket.docs.name
}

output "sql_connection_name" {
  value = google_sql_database_instance.pg.connection_name
}

output "firestore_database" {
  value = google_firestore_database.docs.name
}

output "mongo_url_secret" {
  value = google_secret_manager_secret.s["mongo-url"].secret_id
}

output "frontend_url" {
  value = var.deploy_services ? google_cloud_run_v2_service.frontend[0].uri : null
}

output "mcp_url" {
  value = var.deploy_services ? "${google_cloud_run_v2_service.mcp[0].uri}/mcp" : null
}
