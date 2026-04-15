from api.schemas import ScanTrigger, ComplianceResponse
from agent_core.sub_agents.infra_agent import analyze_infrastructure
from agent_core.sub_agents.identity_agent import analyze_identity  
from tools.aws_scanner import get_rds_config, get_iam_config     
from tools.ticketing_jira import create_jira_ticket
from vault.logger import log_decision
from agent_core.rules_engine import run_layer1_checks

def route_scan_request(trigger: ScanTrigger) -> ComplianceResponse:
    system_name = trigger.system_id.lower()
    
    if "db" in system_name or "database" in system_name:
        real_config = getattr(trigger, 'config_override', None) or get_rds_config(trigger.system_id)
        
        fast_result = run_layer1_checks(trigger.system_id, real_config)
        if fast_result:
            ticket = create_jira_ticket(fast_result.model_dump())
            fast_result.ticket_id = ticket
            decision_dict = fast_result.model_dump()
            decision_dict['system_id'] = trigger.system_id
            log_decision(decision_dict)
            return fast_result
            
        agent_response = analyze_infrastructure(trigger, real_config)
        
        if agent_response.status == "VIOLATION":
            ticket = create_jira_ticket(agent_response.model_dump())
            agent_response.ticket_id = ticket
            
        decision_dict = agent_response.model_dump()
        decision_dict['system_id'] = trigger.system_id
        log_decision(decision_dict) 
        return agent_response
        
    elif "iam" in system_name or "user" in system_name:
        iam_config = getattr(trigger, 'config_override', None) or get_iam_config(trigger.system_id)
        
        fast_result = run_layer1_checks(trigger.system_id, iam_config)
        if fast_result:
            fast_result.assigned_to = "Identity_Team"
            ticket = create_jira_ticket(fast_result.model_dump())
            fast_result.ticket_id = ticket
            decision_dict = fast_result.model_dump()
            decision_dict['system_id'] = trigger.system_id
            log_decision(decision_dict)
            return fast_result
            
        agent_response = analyze_identity(trigger, iam_config)
        
        if agent_response.status == "VIOLATION":
            ticket = create_jira_ticket(agent_response.model_dump())
            agent_response.ticket_id = ticket
            
        decision_dict = agent_response.model_dump()
        decision_dict['system_id'] = trigger.system_id
        log_decision(decision_dict) 
        return agent_response

    else:
        return ComplianceResponse(
            status="PASS",
            violated_rule=None,
            reasoning=f"System ID not recognized for routing: {trigger.system_id}.",
            risk_score=1,
            assigned_to=None,
            ticket_id=None
        )