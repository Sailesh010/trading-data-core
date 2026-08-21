resource "aws_vpc" "this" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true
  tags                  = { Name = var.name }
}

resource "aws_subnet" "private" {
  for_each = { for index, cidr in var.private_subnet_cidrs : index => cidr }

  vpc_id            = aws_vpc.this.id
  cidr_block        = each.value
  availability_zone = var.availability_zones[tonumber(each.key)]
  tags               = { Name = "${var.name}-private-${each.key}" }
}

resource "aws_security_group" "application" {
  name        = "${var.name}-application"
  description = "Application runtime egress"
  vpc_id      = aws_vpc.this.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "database" {
  name        = "${var.name}-database"
  description = "PostgreSQL from application runtime only"
  vpc_id      = aws_vpc.this.id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.application.id]
  }
}

resource "aws_security_group" "redis" {
  name        = "${var.name}-redis"
  description = "Redis from application runtime only"
  vpc_id      = aws_vpc.this.id

  ingress {
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.application.id]
  }
}

resource "aws_security_group" "streaming" {
  name        = "${var.name}-streaming"
  description = "TLS Kafka from application runtime only"
  vpc_id      = aws_vpc.this.id

  ingress {
    from_port       = 9094
    to_port         = 9094
    protocol        = "tcp"
    security_groups = [aws_security_group.application.id]
  }
}
