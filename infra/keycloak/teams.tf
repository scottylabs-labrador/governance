# Parent group for all teams
resource "keycloak_group" "teams" {
  realm_id = keycloak_realm.labrador.id
  name     = "teams"
}

# Team groups
locals {
  team_slugs = toset(keys(var.teams_data))
}

resource "keycloak_group" "team_groups" {
  for_each  = local.team_slugs
  realm_id  = keycloak_realm.labrador.id
  parent_id = keycloak_group.teams.id
  name      = each.key
}

resource "keycloak_group" "team_admins_groups" {
  for_each  = local.team_slugs
  realm_id  = keycloak_realm.labrador.id
  parent_id = keycloak_group.team_groups[each.key].id
  name      = "${each.key}-${var.admin_group_suffix}"
}

# Team memberships
resource "keycloak_group_memberships" "team_memberships" {
  for_each = local.team_slugs
  realm_id = keycloak_realm.labrador.id
  group_id = keycloak_group.team_groups[each.key].id
  members  = var.teams_data[each.key].members
}

resource "keycloak_group_memberships" "team_admins_memberships" {
  for_each = local.team_slugs
  realm_id = keycloak_realm.labrador.id
  group_id = keycloak_group.team_admins_groups[each.key].id
  members  = var.teams_data[each.key].admins
}

# Team OIDC clients
resource "keycloak_openid_client" "team_oidc_clients" {
  for_each  = local.team_slugs
  realm_id  = keycloak_realm.labrador.id
  client_id = "${each.key}-local"

  access_type = "CONFIDENTIAL"

  # Access settings
  root_url            = "http://localhost:3000"
  valid_redirect_uris = ["http://localhost/api/auth/oauth2/callback/keycloak"]
  web_origins         = ["http://localhost"]

  # Capability config
  standard_flow_enabled    = true
  service_accounts_enabled = true

  # Logout settings
  frontchannel_logout_enabled = true
}
