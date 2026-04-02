locals {
  keycloak_realm_url     = "https://idp.scottylabs.org/realms/labrador"
  openbao_oidc_client_id = "openbao"
  secrets_url            = "https://bao.scottylabs.org"
  leadership_group_name  = "leadership"
  admin_suffix           = "admins"

  leadership_data = jsondecode(file("inputs.json")).leadership
  teams_data      = jsondecode(file("inputs.json")).teams
}
