# System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend UI                              │
│                    (http://localhost:8000)                       │
│  • Submit Tickets  • View Agents  • Monitor Circuit Breaker     │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Application                         │
│                         (main.py)                                │
└─────────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────────────┐
│ Milestone 1  │    │ Milestone 2  │    │   Milestone 3        │
│     MVR      │    │  Advanced    │    │  Orchestrator ⭐     │
│              │    │              │    │                      │
│ • TF-IDF     │    │ • DistilBERT │    │ • Semantic Dedup     │
│ • Naive Bayes│    │ • Celery     │    │ • Circuit Breaker    │
│ • Priority Q │    │ • Redis      │    │ • Skill Routing      │
└──────────────┘    └──────────────┘    └──────────────────────┘
```

## Milestone 3 Detailed Flow

```
                    ┌─────────────────┐
                    │  Ticket Arrives │
                    └────────┬────────┘
                             │
                             ▼
        ┌────────────────────────────────────────┐
        │   Step 1: Semantic Deduplication       │
        │                                        │
        │  • Generate sentence embedding         │
        │  • Calculate cosine similarity         │
        │  • Check if similarity > 0.9           │
        │  • Count similar tickets in 5 min      │
        └────────────────┬───────────────────────┘
                         │
                ┌────────┴────────┐
                │                 │
                ▼                 ▼
        ┌──────────────┐   ┌──────────────────┐
        │  Duplicate?  │   │  New Ticket      │
        │              │   │                  │
        │ Create/Link  │   │ Continue to      │
        │ Master       │   │ Step 2           │
        │ Incident     │   │                  │
        └──────────────┘   └────────┬─────────┘
                                    │
                                    ▼
        ┌────────────────────────────────────────┐
        │   Step 2: Circuit Breaker + ML         │
        │                                        │
        │  ┌──────────────────────────────────┐ │
        │  │  Circuit State?                  │ │
        │  └──────┬───────────────────┬───────┘ │
        │         │                   │         │
        │    CLOSED/HALF_OPEN        OPEN       │
        │         │                   │         │
        │         ▼                   ▼         │
        │  ┌─────────────┐    ┌──────────────┐ │
        │  │ Transformer │    │   Baseline   │ │
        │  │   Model     │    │    Model     │ │
        │  │ (DistilBERT)│    │  (TF-IDF)    │ │
        │  └──────┬──────┘    └──────┬───────┘ │
        │         │                   │         │
        │         └───────┬───────────┘         │
        │                 │                     │
        │         Check Latency                 │
        │         > 500ms?                      │
        │                 │                     │
        └─────────────────┼─────────────────────┘
                          │
                          ▼
        ┌────────────────────────────────────────┐
        │   Step 3: Skill-Based Routing          │
        │                                        │
        │  For each available agent:             │
        │    score = skill_match ×               │
        │            capacity_factor ×           │
        │            urgency_weight              │
        │                                        │
        │  Assign to agent with highest score    │
        └────────────────┬───────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────────────┐
        │         Return Response                │
        │                                        │
        │  • Ticket ID                           │
        │  • Category                            │
        │  • Urgency Score                       │
        │  • Model Used                          │
        │  • Assigned Agent                      │
        │  • Master Incident (if duplicate)      │
        └────────────────────────────────────────┘
```

## Circuit Breaker State Machine

```
                    ┌──────────┐
                    │  CLOSED  │ ◄─────────┐
                    │ (Normal) │           │
                    └────┬─────┘           │
                         │                 │
                         │ Latency > 500ms │
                         │ OR              │ 2 successes
                         │ 3 failures      │
                         │                 │
                         ▼                 │
                    ┌──────────┐           │
                    │   OPEN   │           │
                    │(Failover)│           │
                    └────┬─────┘           │
                         │                 │
                         │ After 60s       │
                         │                 │
                         ▼                 │
                    ┌──────────┐           │
                    │HALF_OPEN │───────────┘
                    │ (Testing)│
                    └──────────┘
```

## Semantic Deduplication Algorithm

```
┌─────────────────────────────────────────────────────────┐
│  Recent Tickets Buffer (5-minute sliding window)        │
│                                                         │
│  [Ticket 1] [Ticket 2] [Ticket 3] ... [Ticket N]       │
│     ↓          ↓          ↓              ↓             │
│  [Embed 1] [Embed 2] [Embed 3] ... [Embed N]           │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │  New Ticket Arrives   │
              └───────────┬───────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │  Generate Embedding   │
              │  (all-MiniLM-L6-v2)   │
              └───────────┬───────────┘
                          │
                          ▼
        ┌─────────────────────────────────────┐
        │  Calculate Cosine Similarity with   │
        │  all tickets in buffer              │
        │                                     │
        │  cos(θ) = A·B / (∥A∥ × ∥B∥)        │
        └─────────────────┬───────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────────┐
        │  Count tickets with similarity > 0.9│
        └─────────────────┬───────────────────┘
                          │
                ┌─────────┴─────────┐
                │                   │
                ▼                   ▼
        ┌──────────────┐    ┌──────────────┐
        │  Count < 10  │    │  Count ≥ 10  │
        │              │    │              │
        │ Process      │    │ Create       │
        │ Normally     │    │ Master       │
        │              │    │ Incident     │
        └──────────────┘    └──────────────┘
```

## Skill-Based Routing

```
┌─────────────────────────────────────────────────────────┐
│                    Agent Registry                        │
│                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │  Alice   │  │   Bob    │  │  Carol   │             │
│  │ Tech: 90%│  │ Tech: 80%│  │ Bill: 90%│             │
│  │ Bill: 10%│  │ Bill: 20%│  │ Tech: 10%│             │
│  │ Cap: 3/5 │  │ Cap: 4/5 │  │ Cap: 2/5 │             │
│  └──────────┘  └──────────┘  └──────────┘             │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │  Technical Ticket     │
              │  Urgency: 0.8         │
              └───────────┬───────────┘
                          │
                          ▼
        ┌─────────────────────────────────────┐
        │  Calculate Match Score for Each:    │
        │                                     │
        │  Alice: 0.9 × (3/5) × 1.4 = 0.756  │
        │  Bob:   0.8 × (4/5) × 1.4 = 0.896  │ ← Best
        │  Carol: 0.1 × (2/5) × 1.4 = 0.056  │
        └─────────────────┬───────────────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │  Assign to Bob        │
              │  Reduce capacity: 3/5 │
              └───────────────────────┘
```

## Data Flow

```
User Input
    │
    ▼
┌─────────────┐
│   FastAPI   │
│   Router    │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  Deduplicator   │
│  (Embeddings)   │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Circuit Breaker │
│  (ML Models)    │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Skill Router    │
│ (Optimization)  │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  Agent Queue    │
└─────────────────┘
```

## Component Dependencies

```
main.py
  ├── m1_mvr/
  │   ├── ml_baseline.py
  │   ├── queue_manager.py
  │   └── router.py
  │
  ├── m2_advanced/
  │   ├── ml_transformers.py
  │   ├── celery_worker.py
  │   └── router.py
  │
  └── m3_orchestrator/
      ├── semantic_dedup.py
      │   └── sentence_transformers
      │
      ├── circuit_breaker.py
      │   ├── m1_mvr.ml_baseline
      │   └── m2_advanced.ml_transformers
      │
      ├── skill_router.py
      │   └── scipy.optimize
      │
      └── router.py
          ├── semantic_dedup
          ├── circuit_breaker
          └── skill_router
```

## Technology Stack

```
┌─────────────────────────────────────────┐
│           Presentation Layer            │
│  • HTML/CSS/JavaScript                  │
│  • Jinja2 Templates                     │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────┴───────────────────────┐
│           Application Layer             │
│  • FastAPI (Web Framework)              │
│  • Pydantic (Validation)                │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────┴───────────────────────┐
│            Business Logic               │
│  • Semantic Deduplication               │
│  • Circuit Breaker                      │
│  • Skill-Based Routing                  │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────┴───────────────────────┐
│              ML Layer                   │
│  • scikit-learn (Baseline)              │
│  • Transformers (Advanced)              │
│  • sentence-transformers (Embeddings)   │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────┴───────────────────────┐
│          Infrastructure                 │
│  • Redis (Caching/Locks)                │
│  • Celery (Task Queue)                  │
│  • scipy (Optimization)                 │
└─────────────────────────────────────────┘
```

## Scalability Considerations

```
┌─────────────────────────────────────────────────────┐
│                  Load Balancer                      │
└────────────────────┬────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
   ┌────────┐  ┌────────┐  ┌────────┐
   │FastAPI │  │FastAPI │  │FastAPI │
   │Instance│  │Instance│  │Instance│
   └───┬────┘  └───┬────┘  └───┬────┘
       │           │           │
       └───────────┼───────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
        ▼                     ▼
   ┌────────┐          ┌──────────┐
   │ Redis  │          │  Celery  │
   │Cluster │          │  Workers │
   └────────┘          └──────────┘
```

This architecture supports:
- Horizontal scaling of FastAPI instances
- Distributed caching with Redis
- Async processing with Celery workers
- Circuit breaker prevents cascade failures
- Semantic deduplication reduces load during storms
