import os
import json
import requests
from requests.auth import HTTPBasicAuth
import pip_system_certs.wrapt_requests

def create_jira_ticket(violation_data: dict) -> str:
    jira_url = os.getenv("JIRA_URL")
    jira_email = os.getenv("JIRA_EMAIL")
    jira_token = os.getenv("JIRA_API_TOKEN")

    assigned_team = violation_data.get("assigned_to", "Cloud_Sec_Team")
    
    raci_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../agent_core/raci_matrix.json"))
    with open(raci_path, "r") as f:
        raci = json.load(f)
        
    project_key = raci.get(assigned_team, {}).get("project_key", "SEC")

    summary = f"PCI Violation: Rule {violation_data.get('violated_rule')} on Server"
    description = f"Risk Score: {violation_data.get('risk_score')}\n\nReasoning: {violation_data.get('reasoning')}"

    if not jira_token:
        print("⚠️ JIRA_API_TOKEN not found in .env. Simulating ticket creation...")
        return f"{project_key}-8042"

    payload = {
        "fields": {
            "project": {"key": project_key},
            "summary": summary,
            "description": description,
            "issuetype": {"name": "Bug"}
        }
    }

    try:
        response = requests.post(
            f"{jira_url}/rest/api/2/issue",
            json=payload,
            auth=HTTPBasicAuth(jira_email, jira_token),
            headers={"Accept": "application/json"}
        )
        response.raise_for_status()
        return response.json().get("key")
    except Exception as e:
        print(f"Jira API Error: {e}")
        return f"{project_key}-ERROR"