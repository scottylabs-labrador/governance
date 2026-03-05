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
  default_role   = "default"
  default_policy = "default"
}

# OIDC auth login
resource "vault_jwt_auth_backend" "oidc" {
  path               = "oidc"
  type               = "oidc"
  oidc_discovery_url = var.keycloak_realm_url
  oidc_client_id     = var.oidc_client_id
  oidc_client_secret = var.oidc_client_secret
  default_role       = local.default_role

  # Makes OIDC the default option on the login page
  tune {
    listing_visibility = "unauth"
  }
}

# Default role
resource "vault_jwt_auth_backend_role" "default" {
  backend   = vault_jwt_auth_backend.oidc.path
  role_name = local.default_role
  role_type = "oidc"

  bound_audiences = [var.oidc_client_id]
  user_claim      = "sub"
  groups_claim    = "groups"
  token_policies  = [local.default_policy]

  allowed_redirect_uris = [
    "https://bao.scottylabs.org/ui/vault/auth/oidc/oidc/callback",
    "http://localhost:8250/oidc/callback",
  ]
}

# The default policy initialized in OpenBao.
resource "vault_policy" "default" {
  name   = local.default_policy
  policy = <<-EOT
            # Allow tokens to look up their own properties
            path "auth/token/lookup-self" {
                capabilities = ["read"]
            }
            
            # Allow tokens to renew themselves
            path "auth/token/renew-self" {
                capabilities = ["update"]
            }
            
            # Allow tokens to revoke themselves
            path "auth/token/revoke-self" {
                capabilities = ["update"]
            }
            
            # Allow a token to look up its own capabilities on a path
            path "sys/capabilities-self" {
                capabilities = ["update"]
            }
            
            # Allow a token to look up its own entity by id or name
            path "identity/entity/id/{{identity.entity.id}}" {
              capabilities = ["read"]
            }
            path "identity/entity/name/{{identity.entity.name}}" {
              capabilities = ["read"]
            }
            
            
            # Allow a token to look up its resultant ACL from all policies. This is useful
            # for UIs. It is an internal path because the format may change at any time
            # based on how the internal ACL features and capabilities change.
            path "sys/internal/ui/resultant-acl" {
                capabilities = ["read"]
            }
            
            # Allow a token to renew a lease via lease_id in the request body; old path for
            # old clients, new path for newer
            path "sys/renew" {
                capabilities = ["update"]
            }
            path "sys/leases/renew" {
                capabilities = ["update"]
            }
            
            # Allow looking up lease properties. This requires knowing the lease ID ahead
            # of time and does not divulge any sensitive information.
            path "sys/leases/lookup" {
                capabilities = ["update"]
            }
            
            # Allow a token to manage its own cubbyhole
            path "cubbyhole/*" {
                capabilities = ["create", "read", "update", "delete", "list"]
            }
            
            # Allow a token to wrap arbitrary values in a response-wrapping token
            path "sys/wrapping/wrap" {
                capabilities = ["update"]
            }
            
            # Allow a token to look up the creation time and TTL of a given
            # response-wrapping token
            path "sys/wrapping/lookup" {
                capabilities = ["update"]
            }
            
            # Allow a token to unwrap a response-wrapping token. This is a convenience to
            # avoid client token swapping since this is also part of the response wrapping
            # policy.
            path "sys/wrapping/unwrap" {
                capabilities = ["update"]
            }
            
            # Allow general purpose tools
            path "sys/tools/hash" {
                capabilities = ["update"]
            }
            path "sys/tools/hash/*" {
                capabilities = ["update"]
            }
            
            # Allow a token to make requests to the Authorization Endpoint for OIDC providers.
            path "identity/oidc/provider/+/authorize" {
                capabilities = ["read", "update"]
            }
        EOT
}

