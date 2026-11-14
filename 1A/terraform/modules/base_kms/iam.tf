# base_kms IAM — none here. The key keeps the default (IAM-only) key policy; the app's kms:* grant is in
# base_iam, and each service role grants itself Decrypt / GenerateDataKey in its own module's iam.tf.
