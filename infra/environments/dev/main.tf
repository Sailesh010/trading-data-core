module "network" {
  source = "../../modules/network"

  name               = "trading-data-core-${var.environment}"
  vpc_cidr           = "10.40.0.0/16"
  availability_zones = ["${var.aws_region}a", "${var.aws_region}b"]
  private_subnet_cidrs = [
    "10.40.10.0/24",
    "10.40.20.0/24",
  ]
}

module "database" {
  source = "../../modules/database"

  name              = "trading-data-core-${var.environment}"
  subnet_ids        = module.network.private_subnet_ids
  security_group_id = module.network.database_security_group_id
}

module "redis" {
  source = "../../modules/redis"

  name              = "trading-data-core-${var.environment}"
  subnet_ids        = module.network.private_subnet_ids
  security_group_id = module.network.redis_security_group_id
  auth_token        = var.redis_auth_token
}

module "streaming" {
  source = "../../modules/streaming"

  name              = "trading-data-core-${var.environment}"
  subnet_ids        = module.network.private_subnet_ids
  security_group_id = module.network.streaming_security_group_id
}

module "iam" {
  source = "../../modules/iam"

  name         = "trading-data-core-${var.environment}"
  cluster_arn  = module.streaming.cluster_arn
  cluster_name = module.streaming.cluster_name
}

module "monitoring" {
  source = "../../modules/monitoring"

  name                       = "trading-data-core-${var.environment}"
  database_identifier        = module.database.identifier
  redis_replication_group_id = module.redis.replication_group_id
  msk_cluster_name           = module.streaming.cluster_name
}
