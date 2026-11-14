# modules/base_iam — the role the Java / Python app runs as (ECS task role shown; Lambda is the same idea).
# Foundation: every component module gets var.app_role_id and attaches its own least-privilege policy
# to this role in its iam.tf.
# The role itself is in iam.tf (this component IS identity).
