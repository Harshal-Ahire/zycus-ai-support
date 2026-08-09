from typing import Literal, Optional
from pydantic import BaseModel, Field


class TicketInput(BaseModel):
    subject: str = ""
    body: str


class KBMatch(BaseModel):
    document: str
    section: str
    relevance: float
    excerpt: str


class TriageResult(BaseModel):
    product_area: str
    category: Literal["Bug", "Feature Request", "How-To", "Performance", "Billing", "Integration", "Onboarding", "Data Loss"]
    urgency: Literal["P1", "P2", "P3", "P4"]
    reasoning: str
    known_issue: bool
    knowledge_base_matches: list[KBMatch] = Field(default_factory=list)
    recommended_team: str
    draft_response: str


class AccountHealthRequest(BaseModel):
    account_id: str


class RiskFlag(BaseModel):
    severity: Literal["high", "medium", "low"]
    reason: str
    ticket_id: Optional[str] = None
    quote: Optional[str] = None


class AccountHealthResult(BaseModel):
    account_id: str
    company: str
    executive_summary: str
    open_risks: list[RiskFlag] = Field(default_factory=list)
    talking_points: list[str] = Field(default_factory=list)
    ticket_count_last_90_days: int
    account_found: bool
