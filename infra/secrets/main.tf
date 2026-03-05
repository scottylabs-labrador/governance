# References
# - https://medium.com/@sauravkumarsct/integrate-keycloak-as-oidc-jwt-provider-with-hashicorp-vault-ae9ebcf8e335
# - https://github.com/ScottyLabs/infrastructure/blob/main/tofu/identity/openbao.tf

# Secrets engine
resource "vault_mount" "kv" {
  path = "labrador"
  type = "kv"
  options = {
    version = "2"
  }
}

locals {
  admin_policy_name = "admins"
}
resource "vault_identity_group" "admins" {
  name     = "admins"
  type     = "external"
  policies = [local.admin_policy_name]
}

resource "vault_identity_group_alias" "admins" {
  name           = "admins"
  canonical_id   = vault_identity_group.admins.id
  mount_accessor = vault_jwt_auth_backend.oidc.accessor
}

resource "vault_policy" "admins" {
  name   = local.admin_policy_name
  policy = <<-EOT
    path "*" {
      capabilities = ["create", "read", "update", "delete", "list", "sudo"]
    }

    path "/${vault_mount.kv.path}/metadata/*" {
      capabilities = ["create", "read", "update", "delete", "list", "sudo"]
    }
  EOT
}
