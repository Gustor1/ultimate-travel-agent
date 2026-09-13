"""Standardized agent result envelope for multi-agent execution."""

from typing import Any, Dict, List
from pydantic import BaseModel, Field
from ultimate_travel_agent.models.enums import AgentStatus, VerificationLevel
from ultimate_travel_agent.models.source import SourceReference


class AgentResult(BaseModel):
    """Standardized result produced by every specialized travel sub-agent."""

    agent: str = Field(..., description="Canonical agent name (e.g. 'destination-researcher')")
    status: AgentStatus = Field(default=AgentStatus.COMPLETE, description="Execution status")
    summary: str = Field(..., description="High-level narrative summary of findings")
    findings: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Structured domain data produced by this agent"
    )
    assumptions: List[str] = Field(
        default_factory=list,
        description="Explicit assumptions made due to missing constraints"
    )
    missing_information: List[str] = Field(
        default_factory=list,
        description="Critical gaps or unconfirmed parameters"
    )
    risks: List[str] = Field(
        default_factory=list,
        description="Operational, logistical, or financial risks detected"
    )
    sources: List[SourceReference] = Field(
        default_factory=list,
        description="Authoritative references or documentation consulted"
    )
    verification_level: VerificationLevel = Field(
        default=VerificationLevel.UNVERIFIED,
        description="Overall verification tier of the findings"
    )
