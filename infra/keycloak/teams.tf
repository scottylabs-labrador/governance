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
locals {
  # Generate local-only clients
  local_clients = { for slug in local.team_slugs : "${slug}-local" => {
    client_id   = "${slug}-local"
    root_url    = "http://localhost:3000"
    redirects   = ["http://localhost/api/auth/oauth2/callback/keycloak"]
    web_origins = ["http://localhost"]
  } }

  # Generate prod-ready clients
  prod_clients = { for k, v in var.teams_data : "${k}-prod" => {
    client_id   = "${k}-prod"
    root_url    = v.website
    redirects   = ["${v.server}/api/auth/oauth2/callback/keycloak"]
    web_origins = [v.server]
  } if v.website != "" && v.server != "" }

  # Merge them into one map
  all_clients = merge(local.local_clients, local.prod_clients)
}

resource "keycloak_openid_client" "team_oidc_clients" {
  for_each  = local.all_clients
  realm_id  = keycloak_realm.labrador.id
  client_id = each.value.client_id

  access_type = "CONFIDENTIAL"

  # Access settings
  root_url            = each.value.root_url
  valid_redirect_uris = each.value.redirects
  web_origins         = each.value.web_origins

  # Capability config
  standard_flow_enabled    = true
  service_accounts_enabled = true

  # Logout settings
  frontchannel_logout_enabled = true
}
