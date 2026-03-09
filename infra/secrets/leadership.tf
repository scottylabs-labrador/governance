# A leadership member is allowed to read and write to all secrets.
resource "vault_identity_group" "leadership" {
  name     = var.leadership_group_name
  type     = "external"
  policies = [vault_policy.leadership.name]
}

resource "vault_identity_group_alias" "leadership" {
  name           = var.leadership_group_name
  canonical_id   = vault_identity_group.leadership.id
  mount_accessor = vault_jwt_auth_backend.oidc.accessor
}

resource "vault_policy" "leadership" {
  name   = var.leadership_group_name
  policy = <<-EOT
    path "/${vault_mount.kv.path}/*" {
      capabilities = ["create", "read", "update", "delete", "list", "sudo"]
    }
  EOT
}

# A leadership admin is allowed to manage anything in OpenBao.
locals {
  leadership_admin_group_name = "${var.leadership_group_name}-${var.admin_group_suffix}"
}

resource "vault_identity_group" "leadership_admin" {
  name     = local.leadership_admin_group_name
  type     = "external"
  policies = [vault_policy.leadership_admin.name]
}

resource "vault_identity_group_alias" "leadership_admin" {
  name           = local.leadership_admin_group_name
  canonical_id   = vault_identity_group.leadership_admin.id
  mount_accessor = vault_jwt_auth_backend.oidc.accessor
}

resource "vault_policy" "leadership_admin" {
  name   = local.leadership_admin_group_name
  policy = <<-EOT
    path "*" {
      capabilities = ["create", "read", "update", "delete", "list", "sudo"]
    }

    path "/labrador/metadata/*" {
      capabilities = ["create", "read", "update", "delete", "list", "sudo"]
    }
  EOT
}

