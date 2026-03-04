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

# OIDC auth
resource "vault_jwt_auth_backend" "oidc" {
  path               = "oidc"
  type               = "oidc"
  oidc_discovery_url = "https://idp.scottylabs.org/realms/labrador"
  oidc_client_id     = "openbao"
  oidc_client_secret = var.oidc_client_secret
  default_role       = "default"

  # Makes OIDC the default option on the login page
  tune {
    listing_visibility = "unauth"
  }
}

resource "vault_jwt_auth_backend_role" "default" {
  backend   = vault_jwt_auth_backend.oidc.path
  role_name = "default"
  role_type = "oidc"

  bound_audiences = ["openbao"]
  user_claim      = "sub"
  groups_claim    = "groups"
  token_policies  = ["default"]

  allowed_redirect_uris = [
    "https://bao.scottylabs.org/ui/vault/auth/oidc/oidc/callback",
    "http://localhost:8250/oidc/callback",
  ]
}
