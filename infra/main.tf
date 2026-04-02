module "keycloak" {
  source = "./keycloak"

  # Credentials
  cmu_ldap_bind_credential = var.cmu_ldap_bind_credential
  keycloak_client_id       = var.keycloak_client_id
  keycloak_client_secret   = var.keycloak_client_secret

  # URLs
  keycloak_realm_url = local.keycloak_realm_url
  secrets_url        = local.secrets_url

  # IDs
  openbao_oidc_client_id = local.openbao_oidc_client_id

  # Group names
  admin_group_suffix    = local.admin_suffix
  leadership_group_name = local.leadership_group_name

  # Data
  leadership_data = local.leadership_data
  teams_data      = local.teams_data
}

module "secrets" {
  source = "./secrets"

  # Credentials
  vault_token = var.vault_token

  # OIDC
  oidc_client_id     = local.openbao_oidc_client_id
  oidc_client_secret = module.keycloak.openbao_oidc_client_secret

  # URLs
  keycloak_realm_url = local.keycloak_realm_url
  secrets_url        = local.secrets_url

  # Group names
  admin_group_suffix    = local.admin_suffix
  leadership_group_name = local.leadership_group_name

  # Data
  team_slugs = toset(keys(local.teams_data))
}

module "github" {
  source = "./github"

  # Credentials
  github_token = var.github_token
}
