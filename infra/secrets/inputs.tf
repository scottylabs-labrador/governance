variable "keycloak_realm_url" {
  description = "Keycloak realm URL"
  type        = string
  default     = "https://idp.scottylabs.org/realms/labrador"
}

variable "oidc_client_id" {
  description = "OIDC client ID"
  type        = string
}

variable "oidc_client_secret" {
  description = "OIDC client secret"
  type        = string
  sensitive   = true
}

variable "vault_token" {
  description = "Vault token"
  type        = string
  sensitive   = true
}

