from pydantic import BaseModel, Field
from typing import Literal, Optional, List, Dict, Any
from enum import Enum

class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ActionType(str, Enum):
    SEARCH_KB = "search_kb"
    ISSUE_REFUND = "issue_refund"
    DRAFT_REPLY = "draft_reply"
    ESCALATE = "escalate"
    REQUEST_INFO = "request_info"

class Observation(BaseModel):
    ticket_id: str = Field(..., description="Unique ticket identifier")
    customer_email: str = Field(..., description="Raw customer email content")
    priority: TicketPriority = Field(..., description="Calculated or hinted priority")
    category_hint: Optional[str] = Field(None, description="Optional category from pre-processing")
    conversation_history: List[str] = Field(default_factory=list, description="Previous agent responses")
    knowledge_base_results: List[Dict[str, Any]] = Field(default_factory=list, description="KB search results")
    available_actions: List[ActionType] = Field(..., description="Actions allowed in current state")
    step_count: int = Field(0, description="Current step in episode")
    error_message: Optional[str] = Field(None, description="Last error if any")

class SearchKBAction(BaseModel):
    query: str = Field(..., min_length=3, max_length=200, description="Search query for knowledge base")

class RefundRequest(BaseModel):
    amount: float = Field(..., gt=0, le=10000, description="Refund amount in USD")
    reason: str = Field(..., min_length=5, max_length=500, description="Refund justification")
    order_id: str = Field(..., regex=r'^ORD-\d{6}$', description="Order ID format ORD-XXXXXX")

class DraftReplyAction(BaseModel):
    message: str = Field(..., min_length=10, max_length=2000, description="Draft response to customer")
    send_immediately: bool = Field(False, description="If True, ends episode with success")

class EscalateAction(BaseModel):
    reason: str = Field(..., min_length=10, max_length=500, description="Escalation justification")
    department: Literal["billing", "technical", "fraud", "management"] = Field(..., description="Target department")

class RequestInfoAction(BaseModel):
    question: str = Field(..., min_length=5, max_length=200, description="Question to ask customer")

class Action(BaseModel):
    type: ActionType
    params: Dict[str, Any] = Field(default_factory=dict)

class RewardSignal(BaseModel):
    value: float = Field(..., ge=-1.0, le=1.0)
    reason: str
    step_completion: float = Field(0.0, ge=0.0, le=1.0)

class TaskResult(BaseModel):
    task_id: str
    score: float = Field(..., ge=0.0, le=1.0)
    details: Dict[str, Any]
    passed: bool