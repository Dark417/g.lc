"""Settings for the MongoDB slice (pydantic-settings, env prefix X_MONGODB_).

- Local: mongodb://localhost:27017/?replicaSet=rs0 (1x/local/mongodb, single-node replica set).
- DocumentDB: the cluster endpoint from Terraform output docdb_endpoint with
  tls=true&replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false, plus tls_ca_file.
- Options inside the URI (w, readPreference, retryWrites) win over the defaults in code.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class MongoSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="X_MONGODB_", env_file=".env", extra="ignore")

    uri: str = "mongodb://localhost:27017/?replicaSet=rs0"
    database: str = "xdb"
    app_name: str = "x-mongodb"  # shows up in server logs and currentOp
    max_pool_size: int = 50  # per host; driver default 100
    server_selection_timeout_ms: int = 5000  # "no primary" fails here; driver default 30 s
    max_time_ms: int = 2000  # default maxTimeMS for user-facing queries (no server-side default exists)
    tls_ca_file: str = ""  # DocumentDB: path to global-bundle.pem; PyMongo reads it natively


@lru_cache
def get_mongo_settings() -> MongoSettings:
    return MongoSettings()
