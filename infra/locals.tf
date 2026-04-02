locals {
  leadership_data = jsondecode(file("inputs.json")).leadership
  teams_data      = jsondecode(file("inputs.json")).teams
}
