import httpx
import asyncio

async def trigger_webhook(ticket_id: str, urgency_score: float, category: str):
    """
    Mock Slack/Discord webhook that triggers for any ticket where S > 0.8.
    """
    if urgency_score <= 0.8:
        return

    # In a real scenario, this would be a real URL
    webhook_url = "https://mock.webhook.site/notify"
    
    payload = {
        "text": f"🚨 URGENT TICKET ALERT 🚨\nTicket ID: {ticket_id}\nCategory: {category}\nUrgency Score: {urgency_score:.2f}\nPlease check the dashboard immediately."
    }
    
    # We use httpx for async HTTP requests
    try:
        async with httpx.AsyncClient() as client:
            # We mock the post request to avoid failing if URL is not real
            # Uncomment for real usage:
            # response = await client.post(webhook_url, json=payload)
            # print(f"Webhook triggered: {response.status_code}")
            print(f"Mock Webhook triggered successfully for Ticket {ticket_id} (Score: {urgency_score:.2f})")
    except Exception as e:
        print(f"Failed to trigger webhook: {e}")
