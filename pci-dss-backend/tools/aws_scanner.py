def get_rds_config(system_id: str) -> str:
    mock_aws_environment = {
        "prod-db-01": "RDS Instance: postgres-14. PubliclyAccessible: True. StorageEncrypted: False. VpcSecurityGroups: 0.0.0.0/0 allowed on port 5432.",
        "secure-db-02": "RDS Instance: mysql-8. PubliclyAccessible: False. StorageEncrypted: True. KMSKeyId: alias/aws/rds.",
        "staging-db-01": "RDS Instance: postgres-15. PubliclyAccessible: False. StorageEncrypted: True. TLS 1.2 enforced.",
    }
    return mock_aws_environment.get(system_id, "Resource not found in AWS region.")


def get_iam_config(system_id: str) -> str:
    IAM_MOCK = {
        "prod-iam-01": "User admin01: MFA disabled. Last login: 45 days. Role: Admin+ReadAll.",
        "secure-iam-02": "User svc_read: MFA enabled. Password: 14 chars. Role: ReadOnly.",
        "staging-iam-01": "User dev_user: MFA enabled. Password: 16 chars. Role: Developer. access_review: completed.",
    }
    return IAM_MOCK.get(system_id, "IAM resource not found.")


def get_network_config(system_id: str) -> str:
    NETWORK_MOCK = {
        "prod-net-01": "VPC: vpc-abc123. Inbound: 0.0.0.0/0 on port 443. Outbound: any any. vpc_flow_logs: disabled. firewall: enabled.",
        "secure-net-02": "VPC: vpc-def456. Inbound: 10.0.0.0/8 on port 443. Outbound: 10.0.0.0/8. vpc_flow_logs: enabled. firewall: enabled. segmentation: active.",
        "dmz-net-01": "VPC: vpc-dmz789. Inbound: 0.0.0.0/0 on port 443. dmz: configured. WAF: enabled. firewall: enabled.",
    }
    return NETWORK_MOCK.get(system_id, "Network resource not found.")


def get_encryption_config(system_id: str) -> str:
    ENCRYPTION_MOCK = {
        "prod-tls-01": "TLS 1.0 enabled. TLS 1.2 enabled. Certificate: valid until 2025-12-01. encryption_in_transit: enabled.",
        "secure-tls-02": "TLS 1.2 only. TLS 1.3 enabled. Certificate: valid until 2026-06-15. encryption_in_transit: enabled. HSTS: enabled.",
        "legacy-ssl-01": "SSL 3.0 enabled. TLS 1.0 enabled. certificate_expired. encryption_in_transit: disabled.",
    }
    return ENCRYPTION_MOCK.get(system_id, "Encryption resource not found.")