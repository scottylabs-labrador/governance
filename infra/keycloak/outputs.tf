output "openbao_oidc_client_secret" {
  value     = keycloak_openid_client.openbao.client_secret
  sensitive = true
}
