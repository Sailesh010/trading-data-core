output "private_subnet_ids" { value = values(aws_subnet.private)[*].id }
output "application_security_group_id" { value = aws_security_group.application.id }
output "database_security_group_id" { value = aws_security_group.database.id }
output "redis_security_group_id" { value = aws_security_group.redis.id }
output "streaming_security_group_id" { value = aws_security_group.streaming.id }
