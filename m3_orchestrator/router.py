from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import uuid

from .semantic_dedup import get_deduplicator
from .circuit_breaker import get_circuit_breaker
from .skill_router import get_skill_router
from m1_mvr.ml_baseline import BaselineClassifier, check_urgency
from m2_advanced.ml_transformers import get_classifier

router = APIRouter(prefix="/orchestrator", tags=["Milestone 3 - Autonomous Orchestrator"])

# Initialize components
baseline_classifier = BaselineClassifier()
deduplicator = get_deduplicator()
circuit_breaker = get_circuit_breaker()
skill_router = get_skill_router()

class OrchestratorTicketRequest(BaseModel):
    text: str
    user_id: str

class OrchestratorTicketResponse(BaseModel):
    ticket_id: str
    category: str
    urgency_score: float
    is_duplicate: bool
    master_incident_id: Optional[str]
    model_used: str
    assigned_agent: Optional[dict]
    status: str

@router.post("/ticket", response_model=OrchestratorTicketResponse)
async def process_ticket_orchestrator(request: OrchestratorTicketRequest):
    """
    Milestone 3: Self-healing orchestrator with:
    - Semantic deduplication (ticket storm detection)
    - Circuit breaker (auto-failover to baseline model)
    - Skill-based routing (constraint optimization)
    """
    ticket_id = str(uuid.uuid4())
    
    # Step 1: Semantic Deduplication
    dedup_result = deduplicator.check_ticket(ticket_id, request.text)
    
    if dedup_result["is_duplicate"]:
        # This is part of a ticket storm, suppress individual alert
        return OrchestratorTicketResponse(
            ticket_id=ticket_id,
            category="SUPPRESSED",
            urgency_score=0.0,
            is_duplicate=True,
            master_incident_id=dedup_result["master_incident_id"],
            model_used="none",
            assigned_agent=None,
            status=f"suppressed_under_{dedup_result['master_incident_id']}"
        )
    
    # Step 2: ML Classification with Circuit Breaker
    def primary_model():
        """Transformer model (potentially slow)"""
        advanced_classifier = get_classifier()
        return advanced_classifier.analyze_ticket(request.text)
    
    def fallback_model():
        """Baseline model (fast and reliable)"""
        category = baseline_classifier.predict_category(request.text)
        urgency = check_urgency(request.text)
        return {
            "category": category,
            "urgency_score": 0.9 if urgency else 0.3
        }
    
    # Circuit breaker automatically chooses model based on latency
    ml_result, model_used = circuit_breaker.call(primary_model, fallback_model)
    
    category = ml_result["category"]
    urgency_score = ml_result["urgency_score"]
    
    # Step 3: Skill-Based Routing
    assignment = skill_router.route_ticket(ticket_id, category, urgency_score)
    
    return OrchestratorTicketResponse(
        ticket_id=ticket_id,
        category=category,
        urgency_score=urgency_score,
        is_duplicate=False,
        master_incident_id=None,
        model_used=model_used,
        assigned_agent=assignment,
        status="assigned" if assignment else "queued"
    )

@router.get("/agents")
async def get_agents():
    """Get status of all agents."""
    return {"agents": skill_router.get_agent_status()}

@router.post("/agents/{agent_id}/release")
async def release_agent_capacity(agent_id: str, count: int = 1):
    """Release agent capacity when they complete tickets."""
    skill_router.release_capacity(agent_id, count)
    return {"message": f"Released {count} capacity for agent {agent_id}"}

@router.get("/circuit-breaker/status")
async def get_circuit_status():
    """Get circuit breaker status."""
    return circuit_breaker.get_state()

@router.get("/master-incidents")
async def get_master_incidents():
    """Get all active master incidents."""
    return {
        "master_incidents": deduplicator.master_incidents,
        "recent_ticket_count": len(deduplicator.recent_tickets)
    }
