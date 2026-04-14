from fastapi import FastAPI, HTTPException
from api.schemas import ScanTrigger, ComplianceResponse
from agent_core.router import route_scan_request

app = FastAPI(title="PCI DSS Compliance Microservice")

@app.post("/scan", response_model=ComplianceResponse)
async def run_compliance_scan(trigger: ScanTrigger):
    try:
        result = route_scan_request(trigger)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))