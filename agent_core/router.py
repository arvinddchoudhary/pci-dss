from api.schemas import ScanTrigger, ComplianceResponse
from agent_core.sub_agents.infra_agent import analyze_infrastructure
from tools.aws_scanner import get_rds_config
from tools.ticketing_jira import create_jira_ticket

def route_scan_request(trigger: ScanTrigger) -> ComplianceResponse:
    system_name = trigger.system_id.lower()
    
    if "db" in system_name or "database" in system_name:
        real_config = get_rds_config(trigger.system_id)
        agent_response = analyze_infrastructure(trigger, real_config)
        
        if agent_response.status == "VIOLATION":
            ticket = create_jira_ticket(agent_response.model_dump())
            agent_response.ticket_id = ticket
            
        return agent_response
        
    elif "iam" in system_name or "user" in system_name:
        assigned_team = "Identity_Team"
    else:
        assigned_team = "Cloud_Sec_Team"

    return ComplianceResponse(
        status="PASS",
        violated_rule=None,
        reasoning=f"Mock routing successful for {trigger.system_id}.",
        risk_score=1,
        assigned_to=assigned_team,
        ticket_id=None
    )