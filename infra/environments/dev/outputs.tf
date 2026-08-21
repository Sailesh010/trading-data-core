output "database_endpoint" {
  description = "Private RDS endpoint; not a credential."
  value       = module.database.endpoint
}

output "redis_endpoint" {
  description = "Private Redis primary endpoint."
  value       = module.redis.primary_endpoint
}

output "msk_bootstrap_brokers_tls" {
  description = "TLS bootstrap brokers for application configuration."
  value       = module.streaming.bootstrap_brokers_tls
}

output "application_role_arn" {
  description = "Least-privilege role intended for the application runtime."
  value       = module.iam.application_role_arn
}
