def get_rds_config(system_id: str) -> str:
    mock_aws_environment = {
        "prod-db-01": "RDS Instance: postgres-14. PubliclyAccessible: True. StorageEncrypted: False. VpcSecurityGroups: 0.0.0.0/0 allowed on port 5432.",
        "secure-db-02": "RDS Instance: mysql-8. PubliclyAccessible: False. StorageEncrypted: True. KMSKeyId: alias/aws/rds."
    }
    return mock_aws_environment.get(system_id, "Resource not found in AWS region.")

def get_iam_config(system_id: str) -> str:
    IAM_MOCK = {
        "prod-iam-01": "User admin01: MFA disabled. Last login: 45 days. Role: Admin+ReadAll.",
        "secure-iam-02": "User svc_read: MFA enabled. Password: 14 chars. Role: ReadOnly."
    }
    return IAM_MOCK.get(system_id, "IAM resource not found.")