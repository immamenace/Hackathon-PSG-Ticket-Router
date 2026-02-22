"""
Interactive Demo for Milestone 3
Run this after starting the server to see all features in action
"""
import asyncio
import httpx
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress
import time

console = Console()
BASE_URL = "http://localhost:8000"

async def demo_intro():
    """Show introduction"""
    console.print("\n")
    console.print(Panel.fit(
        "[bold cyan]Milestone 3: The Autonomous Orchestrator[/bold cyan]\n\n"
        "Features:\n"
        "• Semantic Deduplication (Ticket Storm Detection)\n"
        "• Circuit Breaker (Auto-Failover)\n"
        "• Skill-Based Routing (Constraint Optimization)",
        title="🚀 Smart Support Ticket Router",
        border_style="cyan"
    ))
    await asyncio.sleep(2)

async def demo_skill_routing():
    """Demo 1: Skill-based routing"""
    console.print("\n[bold yellow]Demo 1: Skill-Based Routing[/bold yellow]")
    console.print("Submitting tickets with different categories...\n")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        tickets = [
            ("💰 Billing Issue", "I was charged twice for my subscription"),
            ("🔧 Technical Issue", "The API is returning 500 errors"),
            ("⚖️  Legal Question", "Need GDPR compliance documentation"),
        ]
        
        for emoji_title, text in tickets:
            console.print(f"[cyan]Submitting:[/cyan] {emoji_title}")
            
            response = await client.post(
                f"{BASE_URL}/orchestrator/ticket",
                json={"text": text, "user_id": "demo@example.com"}
            )
            result = response.json()
            
            if result['assigned_agent']:
                agent = result['assigned_agent']
                console.print(
                    f"  ✅ Category: [green]{result['category']}[/green] | "
                    f"Assigned to: [bold]{agent['agent_name']}[/bold] | "
                    f"Match Score: {agent['match_score']:.2f}"
                )
            else:
                console.print(f"  ⏳ Queued (no agents available)")
            
            await asyncio.sleep(1)
        
        # Show agent table
        response = await client.get(f"{BASE_URL}/orchestrator/agents")
        agents = response.json()['agents']
        
        table = Table(title="\n📊 Agent Status")
        table.add_column("Agent", style="cyan")
        table.add_column("Technical", style="blue")
        table.add_column("Billing", style="green")
        table.add_column("Legal", style="yellow")
        table.add_column("Capacity", style="magenta")
        
        for agent in agents:
            skills = agent['skills']
            table.add_row(
                agent['name'],
                f"{skills.get('Technical', 0)*100:.0f}%",
                f"{skills.get('Billing', 0)*100:.0f}%",
                f"{skills.get('Legal', 0)*100:.0f}%",
                f"{agent['current_capacity']}/{agent['max_capacity']}"
            )
        
        console.print(table)

async def demo_ticket_storm():
    """Demo 2: Ticket storm detection"""
    console.print("\n[bold yellow]Demo 2: Ticket Storm Detection[/bold yellow]")
    console.print("Simulating a ticket storm (15 similar tickets)...\n")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        storm_text = "URGENT: The login system is completely broken and users cannot access their accounts"
        
        with Progress() as progress:
            task = progress.add_task("[cyan]Submitting tickets...", total=15)
            
            tasks = []
            for i in range(15):
                tasks.append(client.post(
                    f"{BASE_URL}/orchestrator/ticket",
                    json={"text": storm_text, "user_id": f"user{i}@example.com"}
                ))
                progress.update(task, advance=1)
                await asyncio.sleep(0.1)
            
            results = await asyncio.gather(*tasks)
            results = [r.json() for r in results]
        
        # Analyze results
        duplicates = sum(1 for r in results if r['is_duplicate'])
        master_incidents = set(r['master_incident_id'] for r in results if r['master_incident_id'])
        
        console.print(f"\n[green]✅ Ticket Storm Detected![/green]")
        console.print(f"  • Total tickets: {len(results)}")
        console.print(f"  • Duplicates suppressed: {duplicates}")
        console.print(f"  • Master incidents created: {len(master_incidents)}")
        
        if master_incidents:
            for incident_id in master_incidents:
                console.print(f"  • 🚨 Master Incident: [bold red]{incident_id}[/bold red]")

async def demo_circuit_breaker():
    """Demo 3: Circuit breaker"""
    console.print("\n[bold yellow]Demo 3: Circuit Breaker Monitoring[/bold yellow]")
    console.print("Monitoring circuit breaker state during ticket processing...\n")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for i in range(5):
            # Submit ticket
            response = await client.post(
                f"{BASE_URL}/orchestrator/ticket",
                json={
                    "text": f"Test ticket {i+1} for circuit monitoring",
                    "user_id": f"test{i}@example.com"
                }
            )
            result = response.json()
            
            # Get circuit status
            circuit_response = await client.get(f"{BASE_URL}/orchestrator/circuit-breaker/status")
            circuit = circuit_response.json()
            
            # Display status
            state_color = {
                "closed": "green",
                "open": "red",
                "half_open": "yellow"
            }.get(circuit['state'], "white")
            
            console.print(
                f"Ticket {i+1}: "
                f"Model=[cyan]{result['model_used']}[/cyan] | "
                f"Circuit=[{state_color}]{circuit['state'].upper()}[/{state_color}] | "
                f"Failures={circuit['failure_count']}"
            )
            
            await asyncio.sleep(0.5)

async def demo_urgency_detection():
    """Demo 4: Urgency detection"""
    console.print("\n[bold yellow]Demo 4: Urgency Detection[/bold yellow]")
    console.print("Testing urgency scoring...\n")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        test_cases = [
            ("Normal ticket", "I have a question about my account settings"),
            ("Urgent ticket", "CRITICAL: Production database is down and customers are affected!"),
            ("Emergency", "EMERGENCY: Security breach detected, need immediate help ASAP"),
        ]
        
        for label, text in test_cases:
            response = await client.post(
                f"{BASE_URL}/orchestrator/ticket",
                json={"text": text, "user_id": "demo@example.com"}
            )
            result = response.json()
            
            urgency = result['urgency_score']
            urgency_color = "red" if urgency > 0.7 else "yellow" if urgency > 0.4 else "green"
            urgency_label = "🔴 URGENT" if urgency > 0.7 else "🟡 MEDIUM" if urgency > 0.4 else "🟢 NORMAL"
            
            console.print(
                f"[cyan]{label}:[/cyan] "
                f"[{urgency_color}]{urgency_label}[/{urgency_color}] "
                f"(score: {urgency:.2f})"
            )
            
            await asyncio.sleep(0.5)

async def demo_summary():
    """Show final summary"""
    console.print("\n")
    console.print(Panel.fit(
        "[bold green]✅ Demo Complete![/bold green]\n\n"
        "All Milestone 3 features demonstrated:\n"
        "• ✅ Semantic Deduplication\n"
        "• ✅ Circuit Breaker\n"
        "• ✅ Skill-Based Routing\n"
        "• ✅ Urgency Detection\n\n"
        "[cyan]Open http://localhost:8000 for the web interface![/cyan]",
        title="🎉 Success",
        border_style="green"
    ))

async def main():
    """Run all demos"""
    try:
        await demo_intro()
        await demo_skill_routing()
        await asyncio.sleep(1)
        await demo_ticket_storm()
        await asyncio.sleep(1)
        await demo_circuit_breaker()
        await asyncio.sleep(1)
        await demo_urgency_detection()
        await demo_summary()
        
    except httpx.ConnectError:
        console.print("\n[bold red]❌ Error: Cannot connect to server[/bold red]")
        console.print("Please start the server first: [cyan]python main.py[/cyan]")
    except Exception as e:
        console.print(f"\n[bold red]❌ Error: {e}[/bold red]")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted by user[/yellow]")
