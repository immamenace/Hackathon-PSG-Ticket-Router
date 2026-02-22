from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import uuid

from .ml_baseline import BaselineClassifier, check_urgency
from .queue_manager import TicketQueueManager

router = APIRouter(prefix="/mvr", tags=["Milestone 1 - MVR"])

# Initialize ML Model and Queue
classifier = BaselineClassifier()
queue_manager = TicketQueueManager()

class TicketRequest(BaseModel):
    text: str
    user_id: str

class TicketResponse(BaseModel):
    ticket_id: str
    category: str
    urgency: bool
    status: str

@router.post("/ticket", response_model=TicketResponse)
async def process_ticket(request: TicketRequest):
    """
    Synchronous baseline ticket processing endpoint.
    Categorizes the ticket, evaluates urgency, and pushes to a priority queue.
    """
    # 1. Classification
    category = classifier.predict_category(request.text)
    
    # 2. Urgency detection
    urgency = check_urgency(request.text)
    
    # Generate unique ID
    ticket_id = str(uuid.uuid4())
    
    # 3. Queue insertion
    ticket_data = {
        "ticket_id": ticket_id,
        "user_id": request.user_id,
        "text": request.text,
        "category": category,
        "urgency": urgency
    }
    queue_manager.add_ticket(ticket_id, urgency, ticket_data)
    
    return TicketResponse(
        ticket_id=ticket_id,
        category=category,
        urgency=urgency,
        status="queued"
    )

@router.get("/queue/next")
async def get_next_ticket():
    """
    Helper endpoint to pop the most urgent ticket from the queue.
    """
    ticket = queue_manager.get_next_ticket()
    if not ticket:
        return {"message": "Queue is empty"}
    return ticket
