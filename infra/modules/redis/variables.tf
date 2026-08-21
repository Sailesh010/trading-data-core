variable "name" { type = string }
variable "subnet_ids" { type = list(string) }
variable "security_group_id" { type = string }
variable "auth_token" {
  type      = string
  sensitive = true
}
