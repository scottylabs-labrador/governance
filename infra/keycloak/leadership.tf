# Populate the leadership group with members and admins from the `admins.json` file.
# We need to use data sources for roles because we don't have enough permission
# to create composite roles.

# Leadership members group
resource "keycloak_group" "leadership" {
  realm_id = keycloak_realm.labrador.id
  name     = var.leadership_group_name
}

resource "keycloak_group_memberships" "leadership_members" {
  realm_id = keycloak_realm.labrador.id
  group_id = keycloak_group.leadership.id
  members  = var.leadership_data.members
}

data "keycloak_role" "realm_read_only" {
  realm_id = keycloak_realm.labrador.id
  name     = "read-only"
}

resource "keycloak_group_roles" "leadership_members_roles" {
  realm_id = keycloak_realm.labrador.id
  group_id = keycloak_group.leadership.id
  role_ids = [data.keycloak_role.realm_read_only.id]
}

# Leadership admins group
resource "keycloak_group" "leadership_admins" {
  realm_id  = keycloak_realm.labrador.id
  name      = "${var.leadership_group_name}-${var.admin_group_suffix}"
  parent_id = keycloak_group.leadership.id
}

resource "keycloak_group_memberships" "leadership_admins" {
  realm_id = keycloak_realm.labrador.id
  group_id = keycloak_group.leadership_admins.id
  members  = var.leadership_data.admins
}

data "keycloak_role" "realm_admin" {
  realm_id = keycloak_realm.labrador.id
  name     = "admin"
}

resource "keycloak_group_roles" "leadership_admin_roles" {
  realm_id = keycloak_realm.labrador.id
  group_id = keycloak_group.leadership_admins.id
  role_ids = [data.keycloak_role.realm_admin.id]
}
