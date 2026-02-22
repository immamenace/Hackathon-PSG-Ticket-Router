import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass
from scipy.optimize import linear_sum_assignment

@dataclass
class Agent:
    agent_id: str
    name: str
    skill_vector: Dict[str, float]  # e.g., {"Technical": 0.9, "Billing": 0.1, "Legal": 0.0}
    current_capacity: int  # Number of tickets they can still handle
    max_capacity: int = 5

class SkillBasedRouter:
    """
    Maintains a stateful registry of agents with skill vectors.
    Routes tickets to the best available agent using constraint optimization.
    """
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.categories = ["Technical", "Billing", "Legal"]
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize some sample agents with different skill profiles."""
        sample_agents = [
            Agent("agent_1", "Alice", {"Technical": 0.9, "Billing": 0.1, "Legal": 0.0}, 5),
            Agent("agent_2", "Bob", {"Technical": 0.8, "Billing": 0.2, "Legal": 0.0}, 5),
            Agent("agent_3", "Carol", {"Technical": 0.1, "Billing": 0.9, "Legal": 0.0}, 5),
            Agent("agent_4", "Dave", {"Technical": 0.0, "Billing": 0.8, "Legal": 0.2}, 5),
            Agent("agent_5", "Eve", {"Technical": 0.0, "Billing": 0.1, "Legal": 0.9}, 5),
            Agent("agent_6", "Frank", {"Technical": 0.5, "Billing": 0.3, "Legal": 0.2}, 5),
        ]
        for agent in sample_agents:
            self.agents[agent.agent_id] = agent
    
    def add_agent(self, agent: Agent):
        """Add or update an agent in the registry."""
        self.agents[agent.agent_id] = agent
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get agent by ID."""
        return self.agents.get(agent_id)
    
    def _calculate_match_score(self, agent: Agent, category: str, urgency_score: float) -> float:
        """
        Calculate how well an agent matches a ticket.
        Score = skill_match * capacity_factor * urgency_weight
        """
        skill_match = agent.skill_vector.get(category, 0.0)
        
        # Capacity factor: prefer agents with more available capacity
        capacity_factor = agent.current_capacity / agent.max_capacity if agent.max_capacity > 0 else 0
        
        # Urgency weight: urgent tickets get priority matching
        urgency_weight = 1.0 + (0.5 * urgency_score)
        
        # Combined score
        score = skill_match * capacity_factor * urgency_weight
        return score
    
    def route_ticket(self, ticket_id: str, category: str, urgency_score: float) -> Optional[Dict]:
        """
        Route a single ticket to the best available agent.
        Returns agent assignment or None if no agent available.
        """
        available_agents = [a for a in self.agents.values() if a.current_capacity > 0]
        
        if not available_agents:
            return None
        
        # Calculate scores for all available agents
        best_agent = None
        best_score = -1
        
        for agent in available_agents:
            score = self._calculate_match_score(agent, category, urgency_score)
            if score > best_score:
                best_score = score
                best_agent = agent
        
        if best_agent:
            # Assign ticket and reduce capacity
            best_agent.current_capacity -= 1
            return {
                "ticket_id": ticket_id,
                "agent_id": best_agent.agent_id,
                "agent_name": best_agent.name,
                "match_score": best_score,
                "agent_remaining_capacity": best_agent.current_capacity
            }
        
        return None
    
    def route_batch(self, tickets: List[Dict]) -> List[Dict]:
        """
        Route multiple tickets using constraint optimization (Hungarian algorithm).
        tickets: [{"ticket_id": str, "category": str, "urgency_score": float}, ...]
        """
        available_agents = [a for a in self.agents.values() if a.current_capacity > 0]
        
        if not available_agents or not tickets:
            return []
        
        # Build cost matrix (we want to maximize, so use negative scores)
        n_tickets = len(tickets)
        n_agents = len(available_agents)
        cost_matrix = np.zeros((n_tickets, n_agents))
        
        for i, ticket in enumerate(tickets):
            for j, agent in enumerate(available_agents):
                score = self._calculate_match_score(
                    agent, 
                    ticket["category"], 
                    ticket.get("urgency_score", 0.5)
                )
                cost_matrix[i, j] = -score  # Negative because we minimize cost
        
        # Solve assignment problem
        row_ind, col_ind = linear_sum_assignment(cost_matrix)
        
        # Build assignments
        assignments = []
        for ticket_idx, agent_idx in zip(row_ind, col_ind):
            ticket = tickets[ticket_idx]
            agent = available_agents[agent_idx]
            
            if agent.current_capacity > 0:
                agent.current_capacity -= 1
                assignments.append({
                    "ticket_id": ticket["ticket_id"],
                    "agent_id": agent.agent_id,
                    "agent_name": agent.name,
                    "match_score": -cost_matrix[ticket_idx, agent_idx],
                    "agent_remaining_capacity": agent.current_capacity
                })
        
        return assignments
    
    def release_capacity(self, agent_id: str, count: int = 1):
        """Release capacity when an agent completes a ticket."""
        agent = self.agents.get(agent_id)
        if agent:
            agent.current_capacity = min(agent.current_capacity + count, agent.max_capacity)
    
    def get_agent_status(self) -> List[Dict]:
        """Get status of all agents."""
        return [
            {
                "agent_id": a.agent_id,
                "name": a.name,
                "skills": a.skill_vector,
                "current_capacity": a.current_capacity,
                "max_capacity": a.max_capacity,
                "utilization": 1 - (a.current_capacity / a.max_capacity)
            }
            for a in self.agents.values()
        ]

# Global instance
_skill_router = None

def get_skill_router():
    global _skill_router
    if _skill_router is None:
        _skill_router = SkillBasedRouter()
    return _skill_router
