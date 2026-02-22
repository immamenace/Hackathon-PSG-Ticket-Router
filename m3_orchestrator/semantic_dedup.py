import time
from typing import List, Dict
from collections import deque
from sentence_transformers import SentenceTransformer
import numpy as np

class SemanticDeduplicator:
    """
    Detects ticket storms using sentence embeddings and cosine similarity.
    If similarity > 0.9 for more than 10 tickets in 5 minutes, creates a Master Incident.
    """
    def __init__(self, similarity_threshold: float = 0.9, 
                 ticket_threshold: int = 10, 
                 time_window: int = 300):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')  # Lightweight model
        self.similarity_threshold = similarity_threshold
        self.ticket_threshold = ticket_threshold
        self.time_window = time_window  # 5 minutes in seconds
        
        # Store recent tickets with timestamps
        self.recent_tickets = deque(maxlen=100)
        self.master_incidents = {}
        
    def _cosine_similarity(self, vec_a: np.ndarray, vec_b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        return float(np.dot(vec_a, vec_b) / (np.linalg.norm(vec_a) * np.linalg.norm(vec_b)))
    
    def _clean_old_tickets(self):
        """Remove tickets older than the time window."""
        current_time = time.time()
        while self.recent_tickets and (current_time - self.recent_tickets[0]['timestamp']) > self.time_window:
            self.recent_tickets.popleft()
    
    def check_ticket(self, ticket_id: str, text: str) -> Dict:
        """
        Check if this ticket is part of a storm.
        Returns: {
            "is_duplicate": bool,
            "master_incident_id": str or None,
            "similar_count": int
        }
        """
        self._clean_old_tickets()
        
        current_time = time.time()
        embedding = self.model.encode(text)
        
        # Check similarity with recent tickets
        similar_tickets = []
        for ticket in self.recent_tickets:
            similarity = self._cosine_similarity(embedding, ticket['embedding'])
            if similarity > self.similarity_threshold:
                similar_tickets.append(ticket)
        
        # Add current ticket to recent tickets
        self.recent_tickets.append({
            'ticket_id': ticket_id,
            'text': text,
            'embedding': embedding,
            'timestamp': current_time
        })
        
        # Check if we have a ticket storm
        if len(similar_tickets) >= self.ticket_threshold:
            # Create or find master incident
            master_id = None
            for ticket in similar_tickets:
                if ticket['ticket_id'] in self.master_incidents:
                    master_id = self.master_incidents[ticket['ticket_id']]
                    break
            
            if not master_id:
                master_id = f"MASTER-{int(current_time)}"
                
            # Register this ticket under the master incident
            self.master_incidents[ticket_id] = master_id
            
            return {
                "is_duplicate": True,
                "master_incident_id": master_id,
                "similar_count": len(similar_tickets),
                "action": "suppress_alert"
            }
        
        return {
            "is_duplicate": False,
            "master_incident_id": None,
            "similar_count": len(similar_tickets),
            "action": "process_normally"
        }

# Global instance
_deduplicator = None

def get_deduplicator():
    global _deduplicator
    if _deduplicator is None:
        _deduplicator = SemanticDeduplicator()
    return _deduplicator
