resource "aws_sns_topic" "alerts" {
  name = "${var.name}-platform-alerts"
}

resource "aws_cloudwatch_metric_alarm" "database_cpu" {
  alarm_name          = "${var.name}-database-high-cpu"
  namespace           = "AWS/RDS"
  metric_name         = "CPUUtilization"
  statistic           = "Average"
  period              = 300
  evaluation_periods  = 3
  comparison_operator = "GreaterThanThreshold"
  threshold           = 80
  dimensions          = { DBInstanceIdentifier = var.database_identifier }
  alarm_actions       = [aws_sns_topic.alerts.arn]
}

resource "aws_cloudwatch_metric_alarm" "redis_memory" {
  alarm_name          = "${var.name}-redis-low-memory"
  namespace           = "AWS/ElastiCache"
  metric_name         = "DatabaseMemoryUsagePercentage"
  statistic           = "Average"
  period              = 300
  evaluation_periods  = 3
  comparison_operator = "GreaterThanThreshold"
  threshold           = 80
  dimensions          = { ReplicationGroupId = var.redis_replication_group_id }
  alarm_actions       = [aws_sns_topic.alerts.arn]
}

resource "aws_cloudwatch_metric_alarm" "msk_offline_partitions" {
  alarm_name          = "${var.name}-msk-offline-partitions"
  namespace           = "AWS/Kafka"
  metric_name         = "OfflinePartitionsCount"
  statistic           = "Maximum"
  period              = 60
  evaluation_periods  = 2
  comparison_operator = "GreaterThanThreshold"
  threshold           = 0
  dimensions          = { "Cluster Name" = var.msk_cluster_name }
  alarm_actions       = [aws_sns_topic.alerts.arn]
}
