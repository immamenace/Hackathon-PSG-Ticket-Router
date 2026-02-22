import asyncio
import httpx
import uuid

async def fire_request(client, ticket_id):
    payload = {
        "ticket_id": ticket_id,
        "text": "The entire database is deleted and everything is broken! Help ASAP!",
        "user_id": "user_panic"
    }
    # We blast the advanced endpoint
    response = await client.post("http://localhost:8000/advanced/ticket", json=payload)
    return response

async def run_concurrency_test():
    """
    Tests handling 10+ simultaneous requests at the exact same millisecond.
    Requires FastAPI server and Redis to be running.
    """
    ticket_id = f"duplicate-ticket-{uuid.uuid4()}"
    
    async with httpx.AsyncClient() as client:
        # Create 15 identical requests that hit the server at the exact same time
        tasks = [fire_request(client, ticket_id) for _ in range(15)]
        
        print(f"Firing 15 simultaneous requests for ticket {ticket_id}...")
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # We expect exactly ONE 202 Accepted, and 14 409 Conflicts
        accepted_count = 0
        conflict_count = 0
        error_count = 0
        
        for res in results:
            if isinstance(res, Exception):
                error_count += 1
            elif res.status_code == 202:
                accepted_count += 1
            elif res.status_code == 409:
                conflict_count += 1

        print("Results:")
        print(f"  Accepted (202):  {accepted_count}")
        print(f"  Conflicts (409): {conflict_count}")
        print(f"  Errors:          {error_count}")
        
        if accepted_count == 1 and conflict_count == 14:
            print("✅ Concurrency Test PASSED: Atomic locks successfully prevented duplicate processing.")
        else:
            print("❌ Concurrency Test FAILED.")

if __name__ == "__main__":
    asyncio.run(run_concurrency_test())
