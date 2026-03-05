resource "keycloak_ldap_user_federation" "cmu_ldap" {
  # General options
  realm_id = keycloak_realm.labrador.id
  enabled  = true
  name     = "CMU LDAP"
  vendor   = "AD"

  # Connection and authentication settings
  connection_url     = "ldaps://ldap.cmu.edu"
  use_truststore_spi = "ALWAYS"
  connection_pooling = true
  bind_dn            = "uid=scottylabs-svc,ou=andrewperson,dc=andrew,dc=cmu,dc=edu"
  bind_credential    = var.cmu_ldap_bind_password

  # LDAP searching and updating
  edit_mode                 = "UNSYNCED"
  users_dn                  = "ou=andrewperson,dc=andrew,dc=cmu,dc=edu"
  username_ldap_attribute   = "uid"
  rdn_ldap_attribute        = "uid"
  uuid_ldap_attribute       = "guid"
  user_object_classes       = ["cmuAccountPerson,inetOrgPerson"]
  custom_user_search_filter = "(objectClass=cmuAccountPerson)"
  search_scope              = "ONE_LEVEL"

  # Synchronization settings
  import_enabled      = true
  batch_size_for_sync = 0

  # Advanced settings
  trust_email = true
}

# Email attributes
resource "keycloak_ldap_user_attribute_mapper" "email" {
  realm_id                = keycloak_realm.labrador.id
  ldap_user_federation_id = keycloak_ldap_user_federation.cmu_ldap.id
  name                    = "email"
  user_model_attribute    = "email"
  ldap_attribute          = "mail"

  read_only                   = true
  always_read_value_from_ldap = true
  is_mandatory_in_ldap        = true
  attribute_force_default     = true
}

resource "keycloak_ldap_user_attribute_mapper" "full_email" {
  realm_id                = keycloak_realm.labrador.id
  ldap_user_federation_id = keycloak_ldap_user_federation.cmu_ldap.id
  name                    = "full email"
  user_model_attribute    = "fullEmail"
  ldap_attribute          = "eduPersonPrincipalName"

  read_only                   = true
  always_read_value_from_ldap = true
  is_mandatory_in_ldap        = true
  attribute_force_default     = true
}

# Name attributes
resource "keycloak_ldap_user_attribute_mapper" "first_name" {
  realm_id                = keycloak_realm.labrador.id
  ldap_user_federation_id = keycloak_ldap_user_federation.cmu_ldap.id
  name                    = "first name"
  user_model_attribute    = "firstName"
  ldap_attribute          = "givenName"

  read_only                   = true
  always_read_value_from_ldap = true
  is_mandatory_in_ldap        = false
  attribute_force_default     = true
}

resource "keycloak_ldap_user_attribute_mapper" "last_name" {
  realm_id                = keycloak_realm.labrador.id
  ldap_user_federation_id = keycloak_ldap_user_federation.cmu_ldap.id
  name                    = "last name"
  user_model_attribute    = "lastName"
  ldap_attribute          = "sn"

  read_only                   = true
  always_read_value_from_ldap = true
  is_mandatory_in_ldap        = true
  attribute_force_default     = true
}

resource "keycloak_ldap_user_attribute_mapper" "full_name" {
  realm_id                = keycloak_realm.labrador.id
  ldap_user_federation_id = keycloak_ldap_user_federation.cmu_ldap.id
  name                    = "full name"
  user_model_attribute    = "fullName"
  ldap_attribute          = "cn"

  read_only                   = true
  always_read_value_from_ldap = true
  is_mandatory_in_ldap        = true
  attribute_force_default     = true
}

resource "keycloak_ldap_user_attribute_mapper" "display_name" {
  realm_id                = keycloak_realm.labrador.id
  ldap_user_federation_id = keycloak_ldap_user_federation.cmu_ldap.id
  name                    = "display name"
  user_model_attribute    = "displayName"
  ldap_attribute          = "displayName"

  read_only                   = true
  always_read_value_from_ldap = true
  is_mandatory_in_ldap        = true
  attribute_force_default     = true
}

# CMU metadata attributes
resource "keycloak_ldap_user_attribute_mapper" "affiliations" {
  realm_id                = keycloak_realm.labrador.id
  ldap_user_federation_id = keycloak_ldap_user_federation.cmu_ldap.id
  name                    = "affiliations"
  user_model_attribute    = "affiliations"
  ldap_attribute          = "eduPersonAffiliation"

  read_only                   = true
  always_read_value_from_ldap = true
  is_mandatory_in_ldap        = false
  attribute_force_default     = true
}

resource "keycloak_ldap_user_attribute_mapper" "class" {
  realm_id                = keycloak_realm.labrador.id
  ldap_user_federation_id = keycloak_ldap_user_federation.cmu_ldap.id
  name                    = "class"
  user_model_attribute    = "class"
  ldap_attribute          = "cmuStudentClass"

  read_only                   = true
  always_read_value_from_ldap = true
  is_mandatory_in_ldap        = false
  attribute_force_default     = true
}

resource "keycloak_ldap_user_attribute_mapper" "colleges" {
  realm_id                = keycloak_realm.labrador.id
  ldap_user_federation_id = keycloak_ldap_user_federation.cmu_ldap.id
  name                    = "colleges"
  user_model_attribute    = "colleges"
  ldap_attribute          = "eduPersonSchoolCollegeName"

  read_only                   = true
  always_read_value_from_ldap = true
  is_mandatory_in_ldap        = false
  attribute_force_default     = true
}

resource "keycloak_ldap_user_attribute_mapper" "departments" {
  realm_id                = keycloak_realm.labrador.id
  ldap_user_federation_id = keycloak_ldap_user_federation.cmu_ldap.id
  name                    = "departments"
  user_model_attribute    = "departments"
  ldap_attribute          = "cmuDepartment"

  read_only                   = true
  always_read_value_from_ldap = true
  is_mandatory_in_ldap        = false
  attribute_force_default     = true
}

# Creation date attribute
resource "keycloak_ldap_user_attribute_mapper" "creation_date" {
  realm_id                = keycloak_realm.labrador.id
  ldap_user_federation_id = keycloak_ldap_user_federation.cmu_ldap.id
  name                    = "creation date"
  user_model_attribute    = "createTimestamp"
  ldap_attribute          = "whenCreated"

  read_only                   = true
  always_read_value_from_ldap = false
  is_mandatory_in_ldap        = false
  attribute_force_default     = true
}
