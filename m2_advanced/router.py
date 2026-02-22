import os
import redis
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from .celery_worker import process_ticket_task

router = APIRouter(prefix="/advanced", tags=["Milestone 2 - The Intelligent Queue"])

# Connect to Redis for tracking atomic locks
# Using a connection pool for efficiency
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

class AdvancedTicketRequest(BaseModel):
    ticket_id: str  # Client-provided ID to act as idempotency key
    text: str
    user_id: str

class AdvancedTicketResponse(BaseModel):
    message: str
    ticket_id: str
    status: str

@router.post("/ticket", status_code=status.HTTP_202_ACCEPTED, response_model=AdvancedTicketResponse)
async def process_ticket_async(request: AdvancedTicketRequest):
    """
    Asynchronous endpoint returning 202 immediately.
    Implements Redis atomic locks to prevent race conditions on duplicate identical requests.
    """
    # Key for the atomic lock
    lock_key = f"lock:ticket:{request.ticket_id}"

    # We use Redis SETNX (Set if Not eXists) via the `nx=True` parameter.
    # This guarantees that if 10+ requests hit the exact same millisecond, 
    # only ONE will successfully set the key and return True. 
    # We add an expiration time of 300 seconds (5 minutes) so locks don't stay forever.
    acquired_lock = redis_client.set(lock_key, "locked", nx=True, ex=300)

    if not acquired_lock:
        # Atomic lock failed: Another duplicate request is already being processed.
        # We can safely discard this duplicate or return a 409 Conflict.
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ticket {request.ticket_id} is already being processed."
        )

    # If lock acquired safely, we push the job to the celery background queue
    process_ticket_task.delay(
        request.ticket_id,
        request.text,
        request.user_id
    )
    
    return AdvancedTicketResponse(
        message="Ticket accepted for processing.",
        ticket_id=request.ticket_id,
        status="enqueued"
    )
