variable "github_org" {
  description = "GitHub organization"
  type        = string
  default     = "ScottyLabs-Labrador"
}

variable "github_token" {
  description = "GitHub token"
  type        = string
  sensitive   = true
}

variable "members_data" {
  description = "Members data"
  type = object({
    admins     = list(string)
    non_admins = list(string)
  })
}

variable "teams_data" {
  description = "Teams data"
  type = map(object({
    name        = string
    description = string
    members = object({
      andrew_ids       = list(string)
      github_usernames = list(string)
    })
    admins = object({
      andrew_ids       = list(string)
      github_usernames = list(string)
    })
    repos = list(object({
      name        = string
      description = string
    }))
    create_oidc_clients = bool
  }))
}
