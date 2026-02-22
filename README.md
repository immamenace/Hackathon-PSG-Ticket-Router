# 🎫 Smart Support Ticket Router

A high-throughput, intelligent routing engine for SaaS support tickets with semantic deduplication, circuit breakers, and skill-based routing.

![Version](https://img.shields.io/badge/version-3.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-teal)
![License](https://img.shields.io/badge/license-MIT-orange)

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
python main.py

# Open your browser
http://localhost:8000
```

That's it! You now have a fully functional ticket routing system with AI-powered classification, semantic deduplication, and intelligent agent assignment.

## ✨ Features

### 🎯 Milestone 1: MVR (Baseline)
- TF-IDF + Naive Bayes classification
- Regex-based urgency detection
- Priority queue management
- Synchronous processing

### 🧠 Milestone 2: Intelligent Queue
- DistilBERT zero-shot classification
- Sentiment-based urgency scoring
- Async processing with Celery
- Redis atomic locks for idempotency

### 🤖 Milestone 3: Autonomous Orchestrator ⭐
- **Semantic Deduplication**: Detects ticket storms using sentence embeddings
- **Circuit Breaker**: Auto-failover when transformer model is slow (>500ms)
- **Skill-Based Routing**: Constraint optimization for agent assignment
- **Self-Healing**: Automatic recovery and load balancing

## 🎨 Web Interface

Beautiful, modern UI with real-time updates:

- 📝 Submit tickets with instant feedback
- 👥 View agent status and capacity
- 🔌 Monitor circuit breaker state
- 🚨 Track master incidents
- 📊 Live statistics dashboard

## 📊 Key Algorithms

### Semantic Deduplication
```
similarity = cos(θ) = A · B / (∥A∥ × ∥B∥)
```
If similarity > 0.9 for >10 tickets in 5 minutes → Create Master Incident

### Circuit Breaker
```
if latency > 500ms:
    failover_to_baseline_model()
```

### Skill-Based Routing
```
score = skill_match × capacity_factor × urgency_weight
```
Assign to agent with highest score using constraint optimization

## 🧪 Testing

### Run Test Suite
```bash
python test_milestone3.py
```

### Interactive Demo
```bash
python demo_milestone3.py
```

### Test Ticket Storm
```bash
for i in {1..15}; do
  curl -X POST http://localhost:8000/orchestrator/ticket \
    -H "Content-Type: application/json" \
    -d '{"text": "The login system is broken", "user_id": "user'$i'@example.com"}'
done
```

## 📡 API Examples

### Submit a Ticket
```bash
curl -X POST http://localhost:8000/orchestrator/ticket \
  -H "Content-Type: application/json" \
  -d '{
    "text": "URGENT: Production database is down",
    "user_id": "user@example.com"
  }'
```

### Response
```json
{
  "ticket_id": "uuid",
  "category": "Technical",
  "urgency_score": 0.95,
  "is_duplicate": false,
  "master_incident_id": null,
  "model_used": "transformer",
  "assigned_agent": {
    "agent_id": "agent_1",
    "agent_name": "Alice",
    "match_score": 0.85
  },
  "status": "assigned"
}
```

### Get Agent Status
```bash
curl http://localhost:8000/orchestrator/agents
```

### Monitor Circuit Breaker
```bash
curl http://localhost:8000/orchestrator/circuit-breaker/status
```

## 📁 Project Structure

```
.
├── main.py                      # FastAPI application
├── templates/index.html         # Web interface
├── m1_mvr/                      # Milestone 1: Baseline
├── m2_advanced/                 # Milestone 2: Advanced
└── m3_orchestrator/             # Milestone 3: Orchestrator ⭐
    ├── semantic_dedup.py        # Ticket storm detection
    ├── circuit_breaker.py       # Auto-failover
    ├── skill_router.py          # Agent assignment
    └── router.py                # API endpoints
```

## 🎯 Use Cases

### Normal Operations
Tickets are intelligently routed to agents based on:
- Skill match (Technical/Billing/Legal)
- Current capacity
- Urgency level

### Ticket Storm (Outage)
When many similar tickets arrive:
- Semantic deduplication detects the storm
- Master incident is created
- Individual alerts are suppressed
- Reduces noise and improves response

### High Load
When transformer model is slow:
- Circuit breaker activates
- System falls back to baseline model
- Maintains fast response times
- Automatically recovers when stable

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Get started in 5 minutes
- **[README_MILESTONE3.md](README_MILESTONE3.md)** - Detailed feature documentation
- **[USAGE_GUIDE.md](USAGE_GUIDE.md)** - Complete usage instructions
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture diagrams
- **[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)** - Comprehensive overview
- **[MILESTONE3_SUMMARY.md](MILESTONE3_SUMMARY.md)** - Implementation summary

## 🛠️ Technology Stack

- **FastAPI** - Modern web framework
- **scikit-learn** - Baseline ML models
- **Transformers** - Advanced NLP (DistilBERT)
- **sentence-transformers** - Semantic embeddings
- **scipy** - Optimization algorithms
- **Redis** - Caching and locks
- **Celery** - Async task queue

## 🎓 Key Concepts

### Semantic Deduplication
Uses sentence embeddings to understand ticket meaning, not just keywords. Detects similar issues even with different wording.

### Circuit Breaker Pattern
Prevents cascade failures by automatically switching to a fallback when the primary system is slow or failing.

### Constraint Optimization
Uses the Hungarian algorithm to optimally assign multiple tickets to agents, considering skills, capacity, and urgency.

## 📈 Performance

| Component | Latency | Throughput |
|-----------|---------|------------|
| Baseline Model | ~10ms | 100 req/s |
| Transformer Model | ~200ms | 5 req/s |
| Semantic Dedup | ~50ms | 20 req/s |
| Skill Routing | ~5ms | 200 req/s |

## 🔧 Configuration

### Adjust Circuit Breaker
Edit `m3_orchestrator/circuit_breaker.py`:
```python
CircuitBreaker(
    latency_threshold=0.5,    # 500ms
    failure_threshold=3,       # failures before opening
    recovery_timeout=60        # seconds before retry
)
```

### Modify Deduplication
Edit `m3_orchestrator/semantic_dedup.py`:
```python
SemanticDeduplicator(
    similarity_threshold=0.9,  # 90% similarity
    ticket_threshold=10,       # tickets to trigger storm
    time_window=300            # 5 minutes
)
```

### Add Agents
Edit `m3_orchestrator/skill_router.py`:
```python
Agent(
    agent_id="agent_7",
    name="Your Name",
    skill_vector={"Technical": 0.8, "Billing": 0.2, "Legal": 0.0},
    current_capacity=5
)
```

## 🐛 Troubleshooting

### Port Already in Use
```bash
lsof -ti:8000 | xargs kill -9
```

### Missing Dependencies
```bash
pip install --upgrade -r requirements.txt
```

### Slow First Request
The transformer model downloads on first use (~500MB). Subsequent requests are faster.

## 🎉 Demo

Try these scenarios:

1. **Normal Routing**: Submit tickets with different categories
2. **Ticket Storm**: Submit 15 similar tickets rapidly
3. **High Urgency**: Use keywords like "URGENT", "CRITICAL", "DOWN"
4. **Capacity Test**: Submit 30+ tickets to exhaust agents

## 🌟 Highlights

✅ Production-ready code  
✅ Comprehensive testing  
✅ Beautiful UI  
✅ Self-healing system  
✅ Semantic understanding  
✅ Optimal routing  
✅ Real-time monitoring  
✅ Extensive documentation  

## 📝 License

MIT License - Hackathon Project

## 🤝 Contributing

This is a hackathon project, but feel free to fork and extend!

## 📞 Support

- Check the [USAGE_GUIDE.md](USAGE_GUIDE.md) for detailed instructions
- Review [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- See [TROUBLESHOOTING](USAGE_GUIDE.md#troubleshooting) section

---

**Built with ❤️ for the Smart Support Ticket Router Hackathon**

🚀 **Get Started**: `python main.py` → `http://localhost:8000`
