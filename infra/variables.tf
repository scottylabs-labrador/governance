variable "cmu_ldap_bind_credential" {
  description = "CMU LDAP bind password"
  type        = string
  sensitive   = true
}

variable "keycloak_client_id" {
  description = "Keycloak client ID"
  type        = string
  sensitive   = true
}

variable "keycloak_client_secret" {
  description = "Keycloak client secret"
  type        = string
  sensitive   = true
}
variable "vault_token" {
  description = "Vault token"
  type        = string
  sensitive   = true
}
