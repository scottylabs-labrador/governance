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
