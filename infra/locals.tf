locals {
  inputs_data     = jsondecode(file("inputs.json"))
  leadership_data = local.inputs_data["leadership"]
  teams_data      = { for k, v in local.inputs_data : k => v if k != "leadership" }
}
