resource "keycloak_realm" "labrador" {
  realm                       = "labrador"
  default_signature_algorithm = "RS256"
}

