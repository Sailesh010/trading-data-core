resource "aws_elasticache_subnet_group" "this" {
  name       = var.name
  subnet_ids = var.subnet_ids
}

resource "aws_elasticache_replication_group" "this" {
  replication_group_id       = var.name
  description                = "Financial event idempotency claims"
  engine                     = "redis"
  node_type                  = "cache.t4g.micro"
  num_cache_clusters         = 2
  port                       = 6379
  subnet_group_name          = aws_elasticache_subnet_group.this.name
  security_group_ids         = [var.security_group_id]
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  auth_token                 = var.auth_token
  automatic_failover_enabled = true
  multi_az_enabled           = true
  snapshot_retention_limit   = 7
}
