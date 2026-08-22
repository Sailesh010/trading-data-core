# AWS deployment definitions

These Terraform definitions describe, but do not provision, a private AWS
deployment. Amazon RDS for PostgreSQL stores operational records, ElastiCache
for Redis owns idempotency claims, and Amazon MSK carries Kafka-compatible
events. MSK was selected over Kinesis because the application already exposes
a Kafka transport adapter and Kafka consumer-group semantics fit replay and
partition ordering requirements without a second streaming abstraction.

The example `dev` environment keeps service sizing intentionally modest. A
production environment should use a separate root directory and state, multiple
availability zones, reviewed sizing, deletion protection, backup retention, and
organization-specific network connectivity.

## State and secrets

Bootstrap remote state separately: an encrypted, versioned S3 bucket with
bucket policies limiting access to the CI deployment role, plus native S3 state
locking (`use_lockfile = true`). Backend configuration must be supplied during
`terraform init`; it is intentionally not provisioned by this root module.

RDS uses AWS-managed master credentials in Secrets Manager. Redis requires an
auth token supplied through a sensitive Terraform variable by an approved
secret-injection mechanism (for example CI reading Secrets Manager). Never put
the value in a checked-in tfvars file or command history.

Validation only:

```bash
cd infra/environments/dev
terraform fmt -check -recursive ../..
terraform init -backend=false
terraform validate
```

Do not run `terraform apply` without an authorized AWS account, reviewed plan,
remote state, budgets, and production secret delivery.
