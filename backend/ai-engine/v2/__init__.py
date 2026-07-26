"""
VigilX V2 — Multi-Agent Investigation Intelligence Platform
============================================================

20-agent LangGraph pipeline. LLM invoked ONLY at Agent 16 (LLMReasoningAgent).

Development namespace: /ai/v2/ask
Migration target:      /ai/ask  (once V2 is stable and tested)

Agent pipeline:
  1  ConversationManagerAgent   — session + translation
  2  ContextMemoryAgent         — history compression
  3  PlanningAgent              — queries ToolCapabilityRegistry, builds ExecutionPlan
  4  QueryDecompositionAgent    — breaks multi-hop into subtasks
  5  ToolRouterAgent            — event-driven parallel dispatch
  6  SQLToolAgent               — structured REST queries (wraps V1 SQLAgentService)
  7  PythonToolAgent            — deterministic computation (no LLM)
  8  GraphIntelligenceAgent     — Neo4j traversals (wraps V1 graph router)
  9  SemanticRetrievalAgent     — RAG hybrid search (wraps V1 RAGRetriever)
  10 AnalyticsAgent             — timeline, trends, demographics
  11 VisualizationAgent         — chart spec generator
  [FORECAST]  ForecastAgent    — OPTIONAL tool (not in core pipeline)
  12 EvidenceFusionAgent        — merge + deduplicate all tool results
  13 EvidenceRankingAgent       — score + rank every evidence item
  14 CrossValidationAgent       — SQL vs Graph vs RAG consistency check
  15 VerificationAgent          — gate before LLM (prevents hallucination)
  16 LLMReasoningAgent          ← ONLY LLM caller in the entire pipeline
  17 ResponseCriticAgent        — post-LLM self-check (hallucination detection)
  18 CitationAgent              — evidence attribution
  19 RecommendationAgent        — next steps + evidence gaps
  20 ResponseComposerAgent      — final InvestigationResponse assembly
"""
