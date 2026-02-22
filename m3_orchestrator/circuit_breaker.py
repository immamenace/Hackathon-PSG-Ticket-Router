import time
from typing import Callable, Any
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failing, use fallback
    HALF_OPEN = "half_open"  # Testing if service recovered

class CircuitBreaker:
    """
    Circuit breaker pattern implementation.
    If latency exceeds threshold, automatically failover to fallback.
    """
    def __init__(self, latency_threshold: float = 0.5, 
                 failure_threshold: int = 3,
                 recovery_timeout: int = 60):
        self.latency_threshold = latency_threshold  # 500ms
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.success_count = 0
        
    def call(self, primary_func: Callable, fallback_func: Callable, *args, **kwargs) -> tuple[Any, str]:
        """
        Execute primary function with circuit breaker protection.
        Returns: (result, model_used)
        """
        # Check if we should attempt recovery
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
            else:
                # Circuit is open, use fallback immediately
                return fallback_func(*args, **kwargs), "baseline"
        
        # Try primary function
        if self.state in [CircuitState.CLOSED, CircuitState.HALF_OPEN]:
            start_time = time.time()
            try:
                result = primary_func(*args, **kwargs)
                latency = time.time() - start_time
                
                # Check latency threshold
                if latency > self.latency_threshold:
                    self._record_failure()
                    return fallback_func(*args, **kwargs), "baseline"
                else:
                    self._record_success()
                    return result, "transformer"
                    
            except Exception as e:
                self._record_failure()
                return fallback_func(*args, **kwargs), "baseline"
        
        # Should not reach here
        return fallback_func(*args, **kwargs), "baseline"
    
    def _record_failure(self):
        """Record a failure and potentially open the circuit."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            
    def _record_success(self):
        """Record a success and potentially close the circuit."""
        self.failure_count = 0
        
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= 2:  # Need 2 successes to fully recover
                self.state = CircuitState.CLOSED
    
    def get_state(self) -> dict:
        """Get current circuit breaker state."""
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "last_failure_time": self.last_failure_time
        }

# Global instance
_circuit_breaker = None

def get_circuit_breaker():
    global _circuit_breaker
    if _circuit_breaker is None:
        _circuit_breaker = CircuitBreaker()
    return _circuit_breaker
