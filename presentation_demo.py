import requests
import asyncio
import httpx
import uuid
import time

# ANSI Colors for terminal output
CYAN = '\033[96m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
MAGENTA = '\033[95m'
RESET = '\033[0m'

BASE_URL = "http://localhost:8000"

def print_header(title):
    print(f"\n{MAGENTA}{'='*60}")
    print(f"🚀 {title}")
    print(f"{'='*60}{RESET}\n")

def demo_mvr():
    print_header("Milestone 1 (MVR): Synchronous Triage & Priority Queue")
    
    tickets = [
        {"text": "I need help understanding my recent invoice.", "user_id": "Alice", "type": "Normal"},
        {"text": "Is the GDPR privacy policy available anywhere?", "user_id": "Bob", "type": "Normal"},
        {"text": "THE SERVER IS BROKEN! FIX IT ASAP!!", "user_id": "Charlie", "type": "URGENT"},
    ]
    
    print(f"{CYAN}--- 1. Submitting 3 Tickets to MVR ---{RESET}")
    for t in tickets:
        print(f"Submitting ticket from {t['user_id']}: '{t['text']}'")
        response = requests.post(f"{BASE_URL}/mvr/ticket", json={"text": t["text"], "user_id": t["user_id"]})
        data = response.json()
        
        urgency_str = f"{RED}URGENT{RESET}" if data['urgency'] else "Normal"
        print(f"  -> Categorized as: {YELLOW}{data['category']}{RESET} | Priority: {urgency_str}")
        time.sleep(1)

    print(f"\n{CYAN}--- 2. Popping from Priority Queue ---{RESET}")
    print("Even though Charlie's urgent ticket was submitted LAST, it should be processed FIRST.\n")
    
    for i in range(3):
        res = requests.get(f"{BASE_URL}/mvr/queue/next")
        data = res.json()
        print(f"Popped Ticket from {GREEN}{data['user_id']}{RESET} | Category: {data['category']} | Urgent: {data['urgency']}")
        time.sleep(1)

async def fire_request(client, ticket_id):
    payload = {
        "ticket_id": ticket_id,
        "text": "Critical payment failure. We are losing money. Fix ASAP!",
        "user_id": "Eve"
    }
    return await client.post(f"{BASE_URL}/advanced/ticket", json=payload)

async def demo_advanced():
    print_header("Milestone 2 (Intelligent Queue): Concurrency & Background Processing")
    
    print(f"{CYAN}--- 1. Simulating a 'Ticket Storm' (Concurrency) ---{RESET}")
    print("Eve's client is stuck in a loop and sends 15 IDENTICAL requests at the exact same millisecond.")
    print("Redis Atomic Locks will protect the ML worker from duplicates.\n")
    
    ticket_id = f"storm-{uuid.uuid4()}"
    
    async with httpx.AsyncClient() as client:
        # Fire 15 requests concurrently
        tasks = [fire_request(client, ticket_id) for _ in range(15)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, res in enumerate(results):
            if isinstance(res, Exception):
                print(f"Request {i+1:2}: {RED}Error{RESET}")
            elif res.status_code == 202:
                print(f"Request {i+1:2}: {GREEN}202 ACCEPTED{RESET} -> Sent to ML Background Worker")
            elif res.status_code == 409:
                print(f"Request {i+1:2}: {YELLOW}409 CONFLICT{RESET} -> Blocked! Duplicate ticket storm.")
        
        print(f"\n{CYAN}--- 2. Background ML & Webhook Processing ---{RESET}")
        print("Check the terminal where you are running the 'Celery Worker'.")
        print("You will see the DistilBERT model process the 1 accepted ticket and trigger the Mock Discord Webhook!")

if __name__ == "__main__":
    try:
        # Check if server is running
        requests.get(f"{BASE_URL}/health")
        
        # Run Demo
        demo_mvr()
        time.sleep(2)
        asyncio.run(demo_advanced())
        
        print_header("Demo Complete!")
        
    except requests.exceptions.ConnectionError:
        print(f"{RED}ERROR: Could not connect to the server at {BASE_URL}.{RESET}")
        print("Please make sure you have started the FastAPI server:")
        print("  python -m uvicorn main:app --port 8000")
