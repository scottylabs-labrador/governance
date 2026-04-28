# CMU SAML identity provider
resource "keycloak_saml_identity_provider" "cmu_saml" {
  # General settings
  realm        = keycloak_realm.labrador.realm
  alias        = "cmu-saml"
  display_name = "CMU SAML"

  # SAML settings
  entity_id                  = var.keycloak_realm_url
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
  first_broker_login_flow_alias = keycloak_authentication_flow.auto_link_ldap_users.alias
  post_broker_login_flow_alias  = keycloak_authentication_flow.post_login.alias
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

# Username mapper
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

# Auto-link LDAP users flow
resource "keycloak_authentication_flow" "auto_link_ldap_users" {
  realm_id    = keycloak_realm.labrador.id
  alias       = "Auto-link LDAP users"
  description = "Actions taken after first broker login with identity provider account, which is not yet linked to any Keycloak account"
}


# Results in "Invalid username or password." error when this execution is disabled
resource "keycloak_authentication_execution" "create_user_if_unique" {
  realm_id          = keycloak_realm.labrador.id
  parent_flow_alias = keycloak_authentication_flow.auto_link_ldap_users.alias
  authenticator     = "idp-create-user-if-unique"
  requirement       = "ALTERNATIVE"
  priority          = 0
}

resource "keycloak_authentication_execution" "auto_set_existing_user" {
  realm_id          = keycloak_realm.labrador.id
  parent_flow_alias = keycloak_authentication_flow.auto_link_ldap_users.alias
  authenticator     = "idp-auto-link"
  requirement       = "ALTERNATIVE"
  priority          = 1
}

# Post login flow to force the cookies to have a lifetime beyond the users session.
# i.e: reduce the frequency of needing to re-authenticate through CMU SAML.
resource "keycloak_authentication_flow" "post_login" {
  realm_id    = keycloak_realm.labrador.id
  alias       = "SAML post login"
  description = "Post login flow to force the cookies to have a lifetime beyond the users session."
}

resource "keycloak_authentication_execution" "post_login_execution" {
  realm_id          = keycloak_realm.labrador.id
  parent_flow_alias = keycloak_authentication_flow.post_login.alias
  authenticator     = "remember-me-authenticator"
  requirement       = "REQUIRED"
  priority          = 0
}

# Modify the default browser flow to redirect to the CMU SAML provider
resource "keycloak_authentication_flow" "browser" {
  realm_id    = keycloak_realm.labrador.id
  alias       = "browser"
  description = "Browser based authentication"
}

resource "keycloak_authentication_execution" "saml_redirector" {
  realm_id          = keycloak_realm.labrador.id
  parent_flow_alias = keycloak_authentication_flow.browser.alias
  authenticator     = "identity-provider-redirector"
  requirement       = "REQUIRED"
  priority          = 25
}


resource "keycloak_authentication_execution_config" "saml_redirector_config" {
  realm_id     = keycloak_realm.labrador.id
  execution_id = keycloak_authentication_execution.saml_redirector.id
  alias        = "CMU SAML Redirector"
  config = {
    defaultProvider = keycloak_saml_identity_provider.cmu_saml.alias
  }
}
