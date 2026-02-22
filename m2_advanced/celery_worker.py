import os
import asyncio
from celery import Celery
from .ml_transformers import get_classifier
from .webhook import trigger_webhook

# Configure Redis as the broker and backend
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "ticket_routing_worker",
    broker=REDIS_URL,
    backend=REDIS_URL
)

# Load the ML model pipeline once when the worker starts
# (We assume it will be lazy-loaded on the first task, which is fine for this hackathon)
classifier = get_classifier()

@celery_app.task(name="process_ticket_task")
def process_ticket_task(ticket_id: str, text: str, user_id: str):
    """
    Background worker task to process a ticket asynchronously.
    """
    print(f"Processing ticket {ticket_id} for user {user_id}...")
    
    # 1. Classification & Urgency Model Inference
    result = classifier.analyze_ticket(text)
    
    category = result["category"]
    urgency_score = result["urgency_score"]
    
    # 2. Asynchronously Trigger Webhook if S > 0.8
    # Since we are in a sync celery task, we run the async webhook in an event loop
    if urgency_score > 0.8:
        print(f"Ticket {ticket_id} has high urgency ({urgency_score:.2f}). Triggering webhook...")
        asyncio.run(trigger_webhook(ticket_id, urgency_score, category))
    
    print(f"Finished processing ticket {ticket_id}. Category: {category}")
    
    return {
        "ticket_id": ticket_id,
        "category": category,
        "urgency_score": urgency_score,
        "status": "processed"
    }
