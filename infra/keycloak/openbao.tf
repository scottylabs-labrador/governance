# Client that handles OIDC login in OpenBao
# Reference: https://medium.com/@sauravkumarsct/integrate-keycloak-as-oidc-jwt-provider-with-hashicorp-vault-ae9ebcf8e335
resource "keycloak_openid_client" "openbao" {
  realm_id  = keycloak_realm.labrador.id
  client_id = var.openbao_oidc_client_id

  name        = "OpenBao"
  description = "Secrets manager for Labrador"

  access_type = "CONFIDENTIAL"

  # Access settings
  root_url = "${var.secrets_url}/ui/vault/auth/oidc/oidc/callback"
  valid_redirect_uris = [
    "${var.secrets_url}/oidc/callback",
    "${var.secrets_url}/ui/vault/auth/oidc/oidc/callback",
    "http://localhost:8250/oidc/callback"
  ]
  web_origins = [var.secrets_url]
  admin_url   = "${var.secrets_url}/ui/vault/auth/oidc/oidc/callback"

  # Capability config
  standard_flow_enabled    = true
  service_accounts_enabled = true

  # Logout settings
  frontchannel_logout_enabled = true
}

# Groups mapper to send full paths in token
resource "keycloak_openid_group_membership_protocol_mapper" "openbao_groups" {
  realm_id  = keycloak_realm.labrador.id
  client_id = keycloak_openid_client.openbao.id

  name       = "groups"
  claim_name = "groups"
  full_path  = false
}
