from api.schemas import ComplianceResponse

RULES = [
    
    ('TLS 1.0', 'Req 6.4.3', 'TLS 1.0 is deprecated', 9),
    ('TLS 1.1', 'Req 6.4.3', 'TLS 1.1 is deprecated', 8),
    ('0.0.0.0/0', 'Req 1.3.2', 'Public internet access allowed', 10),
    ('StorageEncrypted: False', 'Req 3.4.1', 'No encryption at rest', 9),
    ('PubliclyAccessible: True', 'Req 1.3.2', 'Instance is publicly accessible', 10),
    ('MFA: disabled', 'Req 8.4.2', 'MFA not enabled for account', 9),
    ('critical_unpatched', 'Req 6.3.3', 'Critical patches not applied', 8),
]

def run_layer1_checks(system_id: str, config: str):
    for pattern, rule_id, reason, score in RULES:
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