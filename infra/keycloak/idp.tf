resource "keycloak_saml_identity_provider" "cmu_saml" {
  # General settings
  realm        = keycloak_realm.labrador.realm
  alias        = "cmu-saml"
  display_name = "CMU SAML"

  # SAML settings
  entity_id                  = "https://idp.scottylabs.org/realms/labrador"
  single_sign_on_service_url = "https://login.cmu.edu/idp/profile/SAML2/POST/SSO"

  name_id_policy_format = "Transient"
  principal_type        = "FRIENDLY_ATTRIBUTE"
  principal_attribute   = "eduPersonPrincipalName"

  post_binding_authn_request = true
  post_binding_response      = true
  want_authn_requests_signed = true

  signature_algorithm                    = "RSA_SHA256"
  xml_sign_key_info_key_name_transformer = "KEY_ID"
  validate_signature                     = true

  # Requested AuthnContext Constraints
  authn_context_comparison_type = "exact"

  # Advanced settings
  store_token                   = false
  trust_email                   = true
  first_broker_login_flow_alias = "Auto-link LDAP users"
  sync_mode                     = "FORCE"

  # Couldn't locate in the UI but was present when imported
  login_hint = "false"

  # SAML setting attributes that are not supported as top-level schema attributes
  extra_config = {
    idpEntityId = "https://login.cmu.edu/idp/shibboleth"

    allowCreate = "true"

    metadataDescriptorUrl    = "https://login.cmu.edu/idp/shibboleth"
    useMetadataDescriptorUrl = "true"
  }
}

resource "keycloak_user_template_importer_identity_provider_mapper" "username" {
  realm                   = keycloak_realm.labrador.id
  identity_provider_alias = keycloak_saml_identity_provider.cmu_saml.alias

  name     = "username"
  template = "$${ATTRIBUTE.urn:oid:1.3.6.1.4.1.5923.1.1.1.6 | localpart}"

  extra_config = {
    syncMode = "INHERIT"
    target   = "BROKER_USERNAME"
  }
}
