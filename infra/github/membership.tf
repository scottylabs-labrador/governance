resource "github_membership" "membership_for_admins" {
  for_each = toset(var.members_data.admins)
  username = each.value
  role     = "admin"
}

resource "github_membership" "membership_for_non_admins" {
  for_each = toset(var.members_data.non_admins)
  username = each.value
  role     = "member"
}
