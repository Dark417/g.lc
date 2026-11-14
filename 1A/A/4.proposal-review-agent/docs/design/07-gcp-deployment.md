# 07 · GCP deployment

## Topology

```
                Internet
                   │
          ┌────────▼─────────┐       IAP (Google login, allowlist)
          │ Cloud Run        │
          │ frontend (nginx) │── Direct VPC egress (all traffic) ──┐
          └──────────────────┘                                     │
                                                                   ▼
   MCP clients ──IAM ID token──▶ Cloud Run mcp-server ──VPC──▶ Cloud Run backend (ingress: internal)
                                                                   │
            ┌───────────────┬───────────────┬──────────────┬───────┴──────────┐
            ▼               ▼               ▼              ▼                  ▼
     Cloud SQL PG16    Firestore        GCS bucket     Vertex AI        Secret Manager
     + pgvector        (Mongo compat)   files,         Gemini +         db url, mongo url,
     rules, chunks,    document         artifacts,     embeddings       service token
     sessions, memory  records          inbox/
                                                           ▲
                                  Cloud Run job `ingest` ──┘  (same backend image)
```

## Resources (all in `infra/terraform`)

| Resource | Terraform | Notes |
|---|---|---|
| APIs | `google_project_service` | run, sqladmin, firestore, storage, aiplatform, secretmanager, artifactregistry, iap, compute |
| Artifact Registry | `google_artifact_registry_repository` | Docker repo for 3 images |
| VPC + subnet | `google_compute_network`, `_subnetwork` | Private Google Access on; used by Direct VPC egress |
| Cloud SQL | `google_sql_database_instance` (POSTGRES_16) + db + user | Password generated, stored in Secret Manager |
| Firestore (Mongo compat) | `google_firestore_database` (`database_edition = "ENTERPRISE"`) | Mongo credentials created with gcloud (see DEPLOY), connection string stored as a secret |
| GCS | `google_storage_bucket` | Uniform access, versioning, lifecycle for `inbox/` |
| Secrets | `google_secret_manager_secret` (+ versions) | `database-url`, `mongo-url`, `service-token` |
| Service accounts | backend, frontend, mcp | Least privilege (below) |
| Cloud Run services | `google_cloud_run_v2_service` × 3 | backend internal; frontend IAP; mcp IAM-only |
| Cloud Run job | `google_cloud_run_v2_job` `ingest` | `python -m app.cli ingest gs://BUCKET/inbox` |

### IAM (least privilege)

| SA | Roles |
|---|---|
| backend | `aiplatform.user`, `cloudsql.client`, `datastore.user`, `secretmanager.secretAccessor` (its secrets), `storage.objectAdmin` (bucket only) |
| frontend | none beyond running |
| mcp | `secretmanager.secretAccessor` (service token only) |
| IAP service agent | `run.invoker` on frontend |

## Configuration in GCP

```
GOOGLE_GENAI_USE_VERTEXAI=TRUE   GOOGLE_CLOUD_PROJECT=…   GOOGLE_CLOUD_LOCATION=us-central1
DATABASE_URL=postgresql+asyncpg://app:***@/compliance?host=/cloudsql/PROJECT:REGION:INSTANCE
VECTOR_STORE=pgvector  DOC_STORE=mongo  BLOB_STORE=gcs  GCS_BUCKET=…  EMBEDDER=gemini
ARTIFACT_URI=gs://BUCKET   MEMORY_BACKEND=sql (or vertex)
AUTH_MODE=iap  IAP_AUDIENCE=/projects/NUMBER/locations/REGION/services/frontend
ENABLE_ADK_WEB=false  ADMIN_USERS=you@company.com
```

## Delivery

- `cloudbuild.yaml` builds and pushes the three images, then `gcloud run deploy`s them. Triggered from GitHub or run by hand.
- GitHub Actions (`.github/workflows/4-proposal-review-agent.yml`):
  - PRs: backend tests against real Postgres+pgvector and MongoDB service containers, frontend tests+build, MCP tests, `terraform fmt -check` + `validate`, image builds
  - `main`: optional deploy via Workload Identity Federation when repo variables are set
- Terraform owns infrastructure. CI only changes image tags (`gcloud run deploy --image`), so the two don't fight: `lifecycle.ignore_changes` on the image field.

## Cost (idle-ish, rough)

| Item | Why it costs | Lever |
|---|---|---|
| Cloud SQL | Always-on instance | Smallest custom tier; stop in dev projects |
| Firestore Enterprise | Storage + ops | Tiny at this scale |
| Cloud Run | Per request; min instances 0 | `min_instance_count = 1` on backend only if cold starts hurt |
| Vertex AI | Per token | Flash model; effort on summaries is one call per doc |

## Alternatives considered

- **GKE**: more control, more ops. Cloud Run fits three stateless services + a job.
- **AlloyDB** instead of Cloud SQL: better vector performance at scale; overkill here.
- **Global HTTPS LB + IAP** instead of Cloud Run's built-in IAP: needed for custom domains, Cloud Armor, and path routing. Swap in later without app changes (the backend verifies the same JWT; only the audience changes).
