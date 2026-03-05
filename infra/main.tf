module "keycloak" {
  source                   = "./keycloak"
  keycloak_client_id       = var.keycloak_client_id
  keycloak_client_secret   = var.keycloak_client_secret
  cmu_ldap_bind_credential = var.cmu_ldap_bind_credential
}

module "secrets" {
  source             = "./secrets"
  vault_token        = var.vault_token
  oidc_client_secret = module.keycloak.openbao_oidc_client_secret
}
