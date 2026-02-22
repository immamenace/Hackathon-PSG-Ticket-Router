import heapq
from typing import Dict, Any

class TicketQueueManager:
    """
    In-memory priority queue using heapq.
    Single-threaded execution for Milestone 1.
    """
    def __init__(self):
        # elements in heap will be tuples: (priority, ticket_id, ticket_data)
        # However, we want high urgency to be popped first. 
        # heapq is a min-heap. So we will use negative priority or standard ordering:
        # Priority mapping: High urgency = 1, Normal urgency = 2
        # Then tie-breaker can be counter (insertion order).
        self.queue = []
        self.counter = 0

    def add_ticket(self, ticket_id: str, urgency: bool, data: Dict[str, Any]):
        """
        Add a ticket to the priority queue.
        Urgency=True gets priority 1, else priority 2.
        """
        priority = 1 if urgency else 2
        
        # Tuple: (priority_level, counter, ticket_id, data)
        # Using counter to preserve order among tickets with same priority (FIFO)
        heapq.heappush(self.queue, (priority, self.counter, ticket_id, data))
        self.counter += 1

    def get_next_ticket(self) -> Dict[str, Any]:
        """
        Retrieves the next ticket from the queue with highest priority.
        Returns None if queue is empty.
        """
        if not self.queue:
            return None
        _, _, ticket_id, data = heapq.heappop(self.queue)
        return data

    def __len__(self):
        return len(self.queue)
