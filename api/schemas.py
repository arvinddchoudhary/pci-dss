from pydantic import BaseModel, Field
from typing import Optional

class ScanTrigger(BaseModel):
    system_id: str = Field(..., description="The unique ID of the server to check")
    cloud_provider: str = Field(default="aws", description="aws, azure, or on-prem")
    pci_version: str = Field(default="v4.0", description="PCI DSS version to check against")

class ComplianceResponse(BaseModel):
    status: str = Field(..., description="Either 'PASS' or 'VIOLATION'")
    violated_rule: Optional[str] = Field(None, description="The specific PCI requirement broken")
    reasoning: Optional[str] = Field(None, description="The AI's explanation")
    
    risk_score: Optional[int] = Field(None, ge=1, le=10, description="Severity from 1 to 10")
    assigned_to: Optional[str] = Field(None, description="The RACI team assigned to fix this")
    ticket_id: Optional[str] = Field(None, description="The Jira ticket number created")