"""
Test script for Milestone 3: The Autonomous Orchestrator
Demonstrates semantic deduplication, circuit breaker, and skill-based routing
"""
import asyncio
import httpx
import time
from typing import List, Dict

BASE_URL = "http://localhost:8000"

async def submit_ticket(client: httpx.AsyncClient, text: str, user_id: str) -> Dict:
    """Submit a single ticket"""
    response = await client.post(
        f"{BASE_URL}/orchestrator/ticket",
        json={"text": text, "user_id": user_id}
    )
    return response.json()

async def get_agents(client: httpx.AsyncClient) -> Dict:
    """Get agent status"""
    response = await client.get(f"{BASE_URL}/orchestrator/agents")
    return response.json()

async def get_circuit_status(client: httpx.AsyncClient) -> Dict:
    """Get circuit breaker status"""
    response = await client.get(f"{BASE_URL}/orchestrator/circuit-breaker/status")
    return response.json()

async def get_master_incidents(client: httpx.AsyncClient) -> Dict:
    """Get master incidents"""
    response = await client.get(f"{BASE_URL}/orchestrator/master-incidents")
    return response.json()

async def test_normal_routing():
    """Test 1: Normal ticket routing with skill-based assignment"""
    print("\n" + "="*60)
    print("TEST 1: Normal Routing with Skill-Based Assignment")
    print("="*60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        test_tickets = [
            ("I need help with my invoice and billing", "user1@example.com"),
            ("The API is returning 500 errors", "user2@example.com"),
            ("We need to review the legal contract", "user3@example.com"),
            ("My credit card was charged twice", "user4@example.com"),
            ("The system keeps crashing", "user5@example.com"),
        ]
        
        for text, user_id in test_tickets:
            result = await submit_ticket(client, text, user_id)
            print(f"\n📝 Ticket: {text[:50]}...")
            print(f"   Category: {result['category']}")
            print(f"   Urgency: {result['urgency_score']:.2f}")
            print(f"   Model: {result['model_used']}")
            if result['assigned_agent']:
                agent = result['assigned_agent']
                print(f"   ✅ Assigned to: {agent['agent_name']} (score: {agent['match_score']:.2f})")
            else:
                print(f"   ⏳ Status: {result['status']}")
            
            await asyncio.sleep(0.5)
        
        # Show agent status
        agents = await get_agents(client)
        print("\n" + "-"*60)
        print("Agent Status After Routing:")
        print("-"*60)
        for agent in agents['agents']:
            utilization = agent['utilization'] * 100
            print(f"{agent['name']:10} | Capacity: {agent['current_capacity']}/{agent['max_capacity']} | Utilization: {utilization:.0f}%")

async def test_ticket_storm():
    """Test 2: Semantic deduplication during ticket storm"""
    print("\n" + "="*60)
    print("TEST 2: Ticket Storm Detection (Semantic Deduplication)")
    print("="*60)
    print("Submitting 15 similar tickets rapidly...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Submit many similar tickets
        storm_text = "The login system is completely broken and not working"
        tasks = []
        
        for i in range(15):
            tasks.append(submit_ticket(client, storm_text, f"user{i}@example.com"))
        
        results = await asyncio.gather(*tasks)
        
        # Count duplicates
        duplicates = sum(1 for r in results if r['is_duplicate'])
        master_incidents = set(r['master_incident_id'] for r in results if r['master_incident_id'])
        
        print(f"\n📊 Results:")
        print(f"   Total tickets submitted: {len(results)}")
        print(f"   Duplicates detected: {duplicates}")
        print(f"   Master incidents created: {len(master_incidents)}")
        
        if master_incidents:
            print(f"   🚨 Master Incident IDs: {', '.join(master_incidents)}")
        
        # Show master incidents
        incidents = await get_master_incidents(client)
        print(f"\n   Active master incidents: {len(incidents['master_incidents'])}")
        print(f"   Recent tickets tracked: {incidents['recent_ticket_count']}")

async def test_circuit_breaker():
    """Test 3: Circuit breaker monitoring"""
    print("\n" + "="*60)
    print("TEST 3: Circuit Breaker Status")
    print("="*60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Submit a few tickets and monitor circuit breaker
        for i in range(5):
            text = f"Test ticket {i+1} for circuit breaker monitoring"
            result = await submit_ticket(client, text, f"test{i}@example.com")
            
            circuit = await get_circuit_status(client)
            print(f"\n🔌 After ticket {i+1}:")
            print(f"   Circuit State: {circuit['state']}")
            print(f"   Failure Count: {circuit['failure_count']}")
            print(f"   Model Used: {result['model_used']}")
            
            await asyncio.sleep(0.3)

async def test_diverse_tickets():
    """Test 4: Diverse ticket categories"""
    print("\n" + "="*60)
    print("TEST 4: Diverse Ticket Categories")
    print("="*60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        diverse_tickets = [
            "URGENT: Production server is down and customers cannot access the service",
            "Can you explain the refund policy in the terms of service?",
            "I was charged $99 but my plan should be $49 per month",
            "The API documentation is outdated and missing endpoints",
            "We need GDPR compliance documentation for our legal team",
            "Critical bug: Data loss when saving customer records",
            "How do I update my payment method?",
            "The mobile app crashes on iOS 17",
        ]
        
        results = []
        for text in diverse_tickets:
            result = await submit_ticket(client, text, f"user{len(results)}@example.com")
            results.append(result)
            await asyncio.sleep(0.2)
        
        # Categorize results
        categories = {}
        for result in results:
            cat = result['category']
            categories[cat] = categories.get(cat, 0) + 1
        
        print("\n📊 Category Distribution:")
        for cat, count in categories.items():
            print(f"   {cat}: {count} tickets")
        
        # Show urgency distribution
        urgent = sum(1 for r in results if r['urgency_score'] > 0.7)
        normal = len(results) - urgent
        print(f"\n⚡ Urgency Distribution:")
        print(f"   Urgent (>0.7): {urgent}")
        print(f"   Normal (≤0.7): {normal}")

async def run_all_tests():
    """Run all tests sequentially"""
    print("\n" + "🚀"*30)
    print("MILESTONE 3: AUTONOMOUS ORCHESTRATOR - TEST SUITE")
    print("🚀"*30)
    
    try:
        await test_normal_routing()
        await asyncio.sleep(1)
        
        await test_ticket_storm()
        await asyncio.sleep(1)
        
        await test_circuit_breaker()
        await asyncio.sleep(1)
        
        await test_diverse_tickets()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
        print("="*60)
        print("\n💡 Open http://localhost:8000 to see the web interface!")
        
    except httpx.ConnectError:
        print("\n❌ ERROR: Cannot connect to server")
        print("Please start the server first: python main.py")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(run_all_tests())
