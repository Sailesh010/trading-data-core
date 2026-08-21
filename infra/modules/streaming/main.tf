resource "aws_cloudwatch_log_group" "broker" {
  name              = "/aws/msk/${var.name}"
  retention_in_days = 30
}

resource "aws_msk_cluster" "this" {
  cluster_name           = var.name
  kafka_version          = "3.8.x"
  number_of_broker_nodes = 2

  broker_node_group_info {
    instance_type   = "kafka.t3.small"
    client_subnets  = var.subnet_ids
    security_groups = [var.security_group_id]

    storage_info {
      ebs_storage_info { volume_size = 100 }
    }
  }

  client_authentication {
    sasl { iam = true }
  }

  encryption_info {
    encryption_in_transit { client_broker = "TLS" }
  }

  logging_info {
    broker_logs {
      cloudwatch_logs {
        enabled   = true
        log_group = aws_cloudwatch_log_group.broker.name
      }
    }
  }
}
