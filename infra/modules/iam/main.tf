data "aws_region" "current" {}
data "aws_caller_identity" "current" {}

resource "aws_iam_role" "application" {
  name = "${var.name}-application"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "msk" {
  name = "msk-produce-consume"
  role = aws_iam_role.application.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = ["kafka-cluster:Connect", "kafka-cluster:DescribeCluster"]
        Resource = var.cluster_arn
      },
      {
        Effect = "Allow"
        Action = ["kafka-cluster:ReadData", "kafka-cluster:WriteData", "kafka-cluster:DescribeTopic"]
        Resource = "arn:aws:kafka:${data.aws_region.current.region}:${data.aws_caller_identity.current.account_id}:topic/${var.cluster_name}/*/trades.*"
      },
      {
        Effect = "Allow"
        Action = ["kafka-cluster:AlterGroup", "kafka-cluster:DescribeGroup"]
        Resource = "arn:aws:kafka:${data.aws_region.current.region}:${data.aws_caller_identity.current.account_id}:group/${var.cluster_name}/*/trading-data-*"
      }
    ]
  })
}
