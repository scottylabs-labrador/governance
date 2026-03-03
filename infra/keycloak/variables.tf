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

variable "keycloak_url" {
  description = "Keycloak URL"
  type        = string
  default     = "http://idp.scottylabs.org"
}

variable "keycloak_realm" {
  description = "Keycloak realm"
  type        = string
  default     = "labrador"
}
