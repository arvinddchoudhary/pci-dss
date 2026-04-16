from api.schemas import ScanTrigger, ComplianceResponse
from agent_core.sub_agents.infra_agent import analyze_infrastructure
from agent_core.sub_agents.identity_agent import analyze_identity
from tools.aws_scanner import get_rds_config, get_iam_config, get_network_config, get_encryption_config
from tools.ticketing_jira import create_jira_ticket
from tools.evidence_collector import collect_evidence
from tools.approval_queue import submit_for_approval
from vault.logger import log_decision
from vault.activity_logger import log_agent_activity
from agent_core.rules_engine import run_layer1_checks

# Approval threshold — risk_score >= this requires human-in-the-loop
APPROVAL_THRESHOLD = 8


def route_scan_request(trigger: ScanTrigger) -> ComplianceResponse:
    system_name = trigger.system_id.lower()
    pci_version = getattr(trigger, 'pci_version', 'v4.0')
    
    log_agent_activity("Router", "ROUTE_REQUEST", trigger.system_id,
                       f"Routing scan for {trigger.system_id} (provider={trigger.cloud_provider}, pci={pci_version})")
    
    # === DATABASE / INFRASTRUCTURE ROUTE ===
    if "db" in system_name or "database" in system_name or "rds" in system_name or "sql" in system_name:
        return _handle_infra_scan(trigger, pci_version)
    
    # === IDENTITY / IAM ROUTE ===
    elif "iam" in system_name or "user" in system_name or "identity" in system_name or "auth" in system_name:
        return _handle_iam_scan(trigger, pci_version)
    
    # === NETWORK / FIREWALL ROUTE ===
    elif "net" in system_name or "firewall" in system_name or "fw" in system_name or "vpc" in system_name:
        return _handle_network_scan(trigger, pci_version)
    
    # === ENCRYPTION / TLS / CERTIFICATE ROUTE ===
    elif "tls" in system_name or "cert" in system_name or "encrypt" in system_name or "ssl" in system_name:
        return _handle_encryption_scan(trigger, pci_version)
    
    # === UNKNOWN SYSTEM ===
    else:
        log_agent_activity("Router", "UNRECOGNIZED_SYSTEM", trigger.system_id,
                           f"System ID '{trigger.system_id}' not recognized for routing")
        return ComplianceResponse(
            status="PASS",
            violated_rule=None,
            reasoning=f"System ID not recognized for routing: {trigger.system_id}. No applicable checks.",
            risk_score=1,
            assigned_to=None,
            ticket_id=None
        )


def _handle_infra_scan(trigger: ScanTrigger, pci_version: str) -> ComplianceResponse:
    real_config = getattr(trigger, 'config_override', None) or get_rds_config(trigger.system_id)
    
    # Layer 1: Fast deterministic checks
    fast_result = run_layer1_checks(trigger.system_id, real_config, pci_version)
    if fast_result:
        return _finalize_result(fast_result, trigger, real_config, "Layer1_Infra")
    
    # Layer 2: LLM-based analysis
    log_agent_activity("Router", "ESCALATE_TO_LLM", trigger.system_id, "Layer 1 passed, invoking Infra Agent (LLM)")
    agent_response = analyze_infrastructure(trigger, real_config)
    return _finalize_result(agent_response, trigger, real_config, "Infra_Agent")


def _handle_iam_scan(trigger: ScanTrigger, pci_version: str) -> ComplianceResponse:
    iam_config = getattr(trigger, 'config_override', None) or get_iam_config(trigger.system_id)
    
    fast_result = run_layer1_checks(trigger.system_id, iam_config, pci_version)
    if fast_result:
        fast_result.assigned_to = "Identity_Team"
        return _finalize_result(fast_result, trigger, iam_config, "Layer1_IAM")
    
    log_agent_activity("Router", "ESCALATE_TO_LLM", trigger.system_id, "Layer 1 passed, invoking Identity Agent (LLM)")
    agent_response = analyze_identity(trigger, iam_config)
    return _finalize_result(agent_response, trigger, iam_config, "Identity_Agent")


def _handle_network_scan(trigger: ScanTrigger, pci_version: str) -> ComplianceResponse:
    net_config = getattr(trigger, 'config_override', None) or get_network_config(trigger.system_id)
    
    fast_result = run_layer1_checks(trigger.system_id, net_config, pci_version)
    if fast_result:
        fast_result.assigned_to = "Cloud_Sec_Team"
        return _finalize_result(fast_result, trigger, net_config, "Layer1_Network")
    
    # No dedicated LLM network agent yet — return PASS
    log_agent_activity("Router", "NETWORK_SCAN_PASS", trigger.system_id,
                       "No Layer 1 violations found in network config")
    result = ComplianceResponse(
        status="PASS", violated_rule=None,
        reasoning=f"Network configuration for {trigger.system_id} passed all Layer 1 checks.",
        risk_score=1, assigned_to=None, ticket_id=None
    )
    _log_and_evidence(result, trigger, net_config, "Network_Scanner")
    return result


def _handle_encryption_scan(trigger: ScanTrigger, pci_version: str) -> ComplianceResponse:
    enc_config = getattr(trigger, 'config_override', None) or get_encryption_config(trigger.system_id)
    
    fast_result = run_layer1_checks(trigger.system_id, enc_config, pci_version)
    if fast_result:
        fast_result.assigned_to = "Data_Protection_Team"
        return _finalize_result(fast_result, trigger, enc_config, "Layer1_Encryption")
    
    log_agent_activity("Router", "ENCRYPTION_SCAN_PASS", trigger.system_id,
                       "No Layer 1 violations found in encryption config")
    result = ComplianceResponse(
        status="PASS", violated_rule=None,
        reasoning=f"Encryption configuration for {trigger.system_id} passed all Layer 1 checks.",
        risk_score=1, assigned_to=None, ticket_id=None
    )
    _log_and_evidence(result, trigger, enc_config, "Encryption_Scanner")
    return result


def _finalize_result(result: ComplianceResponse, trigger: ScanTrigger,
                     config: str, agent_name: str) -> ComplianceResponse:
    """Common post-processing: ticket creation, evidence, approval queue, logging."""
    
    if result.status == "VIOLATION":
        # Create Jira ticket
        ticket = create_jira_ticket(result.model_dump())
        result.ticket_id = ticket
        log_agent_activity(agent_name, "TICKET_CREATED", trigger.system_id, f"Jira ticket: {ticket}")
        
        # Submit for human approval if high severity (Constraint C2)
        risk = result.risk_score or 0
        if risk >= APPROVAL_THRESHOLD:
            approval = submit_for_approval(
                system_id=trigger.system_id,
                violated_rule=result.violated_rule or "",
                risk_score=risk,
                reasoning=result.reasoning or "",
                assigned_to=result.assigned_to or "",
                ticket_id=result.ticket_id
            )
            log_agent_activity(agent_name, "APPROVAL_REQUESTED", trigger.system_id,
                               f"High-risk violation (score={risk}) submitted for human approval: {approval['violation_id']}")
    
    _log_and_evidence(result, trigger, config, agent_name)
    return result


def _log_and_evidence(result: ComplianceResponse, trigger: ScanTrigger,
                      config: str, agent_name: str):
    """Log the decision and collect evidence."""
    # Audit log
    decision_dict = result.model_dump()
    decision_dict['system_id'] = trigger.system_id
    log_decision(decision_dict)
    
    # Evidence collection
    collect_evidence(
        system_id=trigger.system_id,
        pci_requirement=result.violated_rule or "N/A",
        config_snapshot=config,
        scan_result=decision_dict,
        evidence_type=f"{agent_name}_scan"
    )