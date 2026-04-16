from api.schemas import ComplianceResponse

# Expanded rules covering all 12 PCI DSS v4.0 domains
RULES = [
    # === Req 1: Network Security Controls ===
    ('0.0.0.0/0', 'Req 1.3.2', 'Public internet access allowed to CDE', 10),
    ('PubliclyAccessible: True', 'Req 1.3.2', 'Instance is publicly accessible from internet', 10),
    ('firewall: disabled', 'Req 1.2.1', 'Network firewall is disabled', 10),
    ('inbound: any any', 'Req 1.3.1', 'Unrestricted inbound traffic allowed', 9),
    ('outbound: any any', 'Req 1.3.4', 'Unrestricted outbound traffic from CDE', 8),
    ('segmentation: none', 'Req 1.4.1', 'No network segmentation in place', 9),
    ('dmz: absent', 'Req 1.4.2', 'No DMZ configured for public-facing systems', 9),
    ('vpc_flow_logs: disabled', 'Req 1.2.5', 'VPC flow logs not enabled', 7),

    # === Req 2: Secure Configurations ===
    ('default_password', 'Req 2.2.2', 'Default password still in use', 10),
    ('default_credentials', 'Req 2.2.2', 'Default credentials not changed', 10),
    ('unnecessary_services: enabled', 'Req 2.2.4', 'Unnecessary services running', 7),
    ('vendor_defaults', 'Req 2.2.1', 'Vendor defaults not removed', 8),
    ('snmp_community: public', 'Req 2.2.5', 'Default SNMP community string in use', 9),
    ('hardening: none', 'Req 2.2.1', 'System hardening not applied', 8),

    # === Req 3: Protect Stored Account Data ===
    ('StorageEncrypted: False', 'Req 3.4.1', 'No encryption at rest for stored data', 9),
    ('encryption_at_rest: disabled', 'Req 3.4.1', 'Encryption at rest not enabled', 9),
    ('pan_stored_plaintext', 'Req 3.5.1', 'PAN stored in plaintext', 10),
    ('full_track_data_stored', 'Req 3.3.1', 'Full track data stored after authorization', 10),
    ('cvv_stored', 'Req 3.3.2', 'CVV/CVC stored after authorization', 10),
    ('kms: none', 'Req 3.6.1', 'No key management system in place', 8),
    ('key_rotation: never', 'Req 3.7.1', 'Cryptographic key rotation never performed', 8),
    ('data_retention: unlimited', 'Req 3.2.1', 'No data retention policy enforced', 7),
    ('masking: none', 'Req 3.4.2', 'PAN not masked when displayed', 8),

    # === Req 4: Protect Data in Transit ===
    ('TLS 1.0', 'Req 4.2.1', 'TLS 1.0 is deprecated and insecure', 9),
    ('TLS 1.1', 'Req 4.2.1', 'TLS 1.1 is deprecated and insecure', 8),
    ('SSL 3.0', 'Req 4.2.1', 'SSL 3.0 is deprecated and insecure', 10),
    ('certificate_expired', 'Req 4.2.1', 'TLS certificate has expired', 9),
    ('certificate_self_signed', 'Req 4.2.1', 'Self-signed certificate in production CDE', 7),
    ('encryption_in_transit: disabled', 'Req 4.2.1', 'Data in transit not encrypted', 10),
    ('http_only', 'Req 4.2.1', 'HTTP without TLS used for cardholder data', 10),

    # === Req 5: Protect Against Malware ===
    ('antivirus: disabled', 'Req 5.3.1', 'Anti-malware solution not active', 9),
    ('antimalware: disabled', 'Req 5.3.1', 'Anti-malware protection disabled', 9),
    ('malware_signatures: outdated', 'Req 5.3.2', 'Malware signatures not up to date', 8),
    ('real_time_scan: disabled', 'Req 5.3.3', 'Real-time malware scanning disabled', 8),
    ('edr: disabled', 'Req 5.3.1', 'Endpoint detection and response not enabled', 7),

    # === Req 6: Develop Secure Systems ===
    ('critical_unpatched', 'Req 6.3.3', 'Critical security patches not applied', 8),
    ('high_unpatched', 'Req 6.3.3', 'High severity patches not applied within 30 days', 7),
    ('patch_status: outdated', 'Req 6.3.3', 'System patches are outdated', 8),
    ('waf: disabled', 'Req 6.4.1', 'Web application firewall not enabled', 8),
    ('waf: absent', 'Req 6.4.1', 'No WAF protecting public-facing web applications', 8),
    ('code_review: none', 'Req 6.3.1', 'No code review process for custom software', 7),
    ('vuln_scan: failed', 'Req 6.5.4', 'Vulnerability scan failed', 8),
    ('sql_injection', 'Req 6.2.4', 'SQL injection vulnerability detected', 9),
    ('xss_detected', 'Req 6.2.4', 'Cross-site scripting vulnerability detected', 8),

    # === Req 7: Restrict Access ===
    ('access: unrestricted', 'Req 7.2.1', 'Access to CDE not restricted by business need', 9),
    ('role_based_access: disabled', 'Req 7.2.2', 'Role-based access control not implemented', 8),
    ('privilege: admin_all', 'Req 7.2.1', 'Excessive admin privileges granted', 8),
    ('access_review: never', 'Req 7.2.4', 'User access reviews not performed', 7),
    ('shared_accounts', 'Req 7.2.6', 'Shared/generic accounts in use for CDE access', 9),

    # === Req 8: Identify Users and Authenticate ===
    ('MFA: disabled', 'Req 8.4.2', 'MFA not enabled for CDE access', 9),
    ('mfa: disabled', 'Req 8.4.2', 'Multi-factor authentication not enabled', 9),
    ('password_length: short', 'Req 8.3.6', 'Password length below 12 characters minimum', 7),
    ('password_policy: none', 'Req 8.3.6', 'No password policy enforced', 8),
    ('inactive_account', 'Req 8.2.6', 'Inactive account not disabled within 90 days', 7),
    ('lockout: disabled', 'Req 8.3.4', 'Account lockout not enabled after failed attempts', 7),
    ('session_timeout: none', 'Req 8.2.8', 'No session idle timeout configured', 6),
    ('shared_password', 'Req 8.2.2', 'Shared passwords in use', 9),
    ('service_account_password: never_rotated', 'Req 8.6.3', 'Service account password never rotated', 8),

    # === Req 9: Physical Access ===
    ('physical_access: unrestricted', 'Req 9.4.1', 'Physical access to CDE not restricted', 9),
    ('badge_system: disabled', 'Req 9.2.1', 'Badge access system disabled', 8),
    ('visitor_log: absent', 'Req 9.3.1', 'No visitor log maintained', 7),
    ('media_destruction: none', 'Req 9.4.7', 'No media destruction policy', 7),

    # === Req 10: Log and Monitor ===
    ('logging: disabled', 'Req 10.2.1', 'Audit logging not enabled', 10),
    ('audit_log: disabled', 'Req 10.2.1', 'Audit logging disabled on CDE system', 10),
    ('log_retention: insufficient', 'Req 10.7.1', 'Log retention less than 12 months', 7),
    ('log_monitoring: none', 'Req 10.4.1', 'No log monitoring or alerting in place', 8),
    ('siem: disconnected', 'Req 10.4.1', 'SIEM not connected to CDE logs', 8),
    ('ntp: disabled', 'Req 10.6.1', 'Time synchronization not configured', 6),
    ('log_integrity: none', 'Req 10.3.2', 'No log integrity monitoring', 7),

    # === Req 11: Test Security Regularly ===
    ('pentest: overdue', 'Req 11.4.1', 'Penetration test overdue', 8),
    ('vuln_scan_external: overdue', 'Req 11.3.2', 'External vulnerability scan overdue', 8),
    ('vuln_scan_internal: overdue', 'Req 11.3.1', 'Internal vulnerability scan overdue', 7),
    ('ids: disabled', 'Req 11.5.1', 'Intrusion detection system disabled', 8),
    ('file_integrity: disabled', 'Req 11.5.2', 'File integrity monitoring disabled', 8),
    ('wireless_scan: never', 'Req 11.2.1', 'Wireless access point scan never performed', 6),

    # === Req 12: Organizational Policies ===
    ('security_policy: absent', 'Req 12.1.1', 'No information security policy', 8),
    ('risk_assessment: overdue', 'Req 12.3.1', 'Annual risk assessment not performed', 7),
    ('security_awareness: none', 'Req 12.6.1', 'No security awareness training program', 7),
    ('incident_response: absent', 'Req 12.10.1', 'No incident response plan', 9),
    ('ir_plan: untested', 'Req 12.10.2', 'Incident response plan not tested annually', 7),
    ('third_party_risk: unassessed', 'Req 12.8.1', 'Third-party service provider risk not assessed', 7),
]

# v3.2.1 specific rules (for transition period support per Constraint C4)
RULES_V321 = [
    ('TLS 1.0', 'Req 2.3', 'TLS 1.0 deprecated under v3.2.1', 9),
    ('TLS 1.1', 'Req 2.3', 'TLS 1.1 deprecated under v3.2.1', 8),
    ('StorageEncrypted: False', 'Req 3.4', 'Disk encryption not in place (v3.2.1)', 9),
    ('MFA: disabled', 'Req 8.3', 'MFA not enabled (v3.2.1)', 9),
    ('0.0.0.0/0', 'Req 1.3', 'Public access to CDE (v3.2.1)', 10),
    ('logging: disabled', 'Req 10.2', 'Audit logging disabled (v3.2.1)', 10),
    ('antivirus: disabled', 'Req 5.1', 'Anti-virus not deployed (v3.2.1)', 9),
    ('firewall: disabled', 'Req 1.1', 'Firewall not configured (v3.2.1)', 10),
]


def run_layer1_checks(system_id: str, config: str, pci_version: str = "v4.0"):
    """Run deterministic pattern-matching checks. Returns first violation found or None."""
    
    # Select ruleset based on PCI version
    active_rules = RULES if pci_version == "v4.0" else RULES_V321
    
    for pattern, rule_id, reason, score in active_rules:
        if pattern.lower() in config.lower():
            return ComplianceResponse(
                status='VIOLATION',
                violated_rule=rule_id,
                reasoning=f'Layer 1 fast check: {reason} violates {rule_id}',
                risk_score=score,
                assigned_to='Cloud_Sec_Team',
                ticket_id=None
            )
    return None