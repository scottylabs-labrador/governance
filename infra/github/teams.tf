resource "github_team" "teams" {
  for_each    = var.teams_data
  name        = each.value.name
  description = each.value.description
  privacy     = "closed" # Visible to all members of the organization
}
