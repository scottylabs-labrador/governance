# Labrador realm
resource "keycloak_realm" "labrador" {
  realm                       = "labrador"
  display_name                = "Labrador"
  default_signature_algorithm = "RS256"
  remember_me                 = true
}
