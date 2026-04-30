locals {
  inputs_data               = jsondecode(file("inputs.json"))
  teams_data                = local.inputs_data["teams"]
  leadership_team_data      = local.teams_data["leadership"]
  non_leadership_teams_data = { for k, v in local.teams_data : k => v if k != "leadership" }
}
