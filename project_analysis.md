# VigilX Backend System Discovery and Analysis Report

This document provides a comprehensive, deep-dive architectural and system analysis of the **VigilX-BE** (VigilX Backend) repository. It outlines the codebase structure, technical designs, API systems, database schemas, AI integrations, security mechanisms, and identifies critical implementation gaps.

---

## 1. Executive Summary

**VigilX** is a crime intelligence and First Information Report (FIR) analysis platform designed for police departments and investigative authorities. The backend repository (`VigilX-BE`) comprises two principal server applications:
1. **Django API Server (`backend/django-api`)**: Manages the core relational database operations, user records, and role-based permissions (RBAC). It exposes REST endpoints for case data, victim profiles, suspect profiles, investigation logs, and automated PDF report generation.
2. **FastAPI AI Engine (`backend/ai-engine`)**: Acts as a natural language crime intelligence interface. It parses user questions, identifies intent, runs logical reasoning flows over case documents using LangGraph (and state-machine fallbacks), merges REST-based structured records, and utilizes an LLM to generate evidence-grounded answers.

The system is configured to integrate relational (PostgreSQL), graph (Neo4j), and vector (Qdrant) data models to support multidimensional crime query capability.

---

## 2. Core Problem and Product Purpose

### A. One-line description
VigilX is a multi-database, role-based crime intelligence platform that exposes secure case records and embeds a natural-language AI agent for structured, evidence-grounded investigation analysis.

### B. Short description
Police investigations suffer from fragmented records across relational databases, unconnected networks of co-accused in graphs, and unstructured text facts. VigilX addresses this by centralizing police FIR records, modeling suspect associations in a graph database, vectorizing facts for similarity retrieval, and providing investigators with a conversational AI agent that generates audit-logged, role-redacted insights.

### C. Detailed product explanation
VigilX provides an administrative and investigative portal for law enforcement agencies. Investigators record FIR data, create case diary entries (Investigation Logs), and associate entities (like phone numbers or vehicles) with crimes. Crime analysts utilize graph-based network traversals to identify potential organized crime syndicates. Supervisors oversee investigations and monitor system actions via an immutable audit trail. Policymakers query aggregate statistics without accessing raw PII (Personally Identifiable Information) because the system dynamically redacts phone numbers, addresses, and statements.

### D. Problem being solved
* **Fragmented Evidence**: Traditional police databases separate case files, suspect relationships, and unstructured briefs.
* **Unauthorized PII Access**: High-level policymakers need to analyze crime trends without exposing sensitive details (addresses, phone numbers) of victims and suspect statements.
* **Complex Data Queries**: Investigators are not SQL experts; they require natural language access to complex case timelines and suspect networks.
* **Audit Trail Requirements**: Internal security requires strict auditing of mutating database queries and login activities.

### E. Target users
* **Investigators**: Field officers adding cases, creating case diaries, and searching suspect connections.
* **Crime Analysts**: Specialists running syndicate-detection and co-accused graphs.
* **Supervisors**: Administrators managing user accounts, checking the audit trail, and downloading reports.
* **Policymakers**: Strategic leaders querying crime statistics and trends.

### F. Main user journeys
1. **Investigation Intake**: Investigator authenticates $\rightarrow$ logs FIR $\rightarrow$ associates accused, victims, and clue entities.
2. **Case Diary Documentation**: Investigator records progress in the `InvestigationLog` $\rightarrow$ system automatically logs the active user and timestamps the entry.
3. **Conversational AI Analysis**: Investigator queries: *"Show details about suspect Rajesh Kumar"* $\rightarrow$ AI Engine classifies intent $\rightarrow$ retrieves data $\rightarrow$ formats evidence $\rightarrow$ answers with citations.
4. **Graph-based Lead Discovery**: Analyst searches a case $\rightarrow$ AI recommends suspects by traversing 2nd-degree co-accused relationships.
5. **Supervisor Auditing**: Supervisor retrieves system logs $\rightarrow$ inspects IP addresses, timestamps, and request bodies (passwords sanitized).

---

## 3. Current Technology Stack

Based on configurations and dependency files:

### Frontend
* **Unable to confirm from the existing project**: The workspace contains no frontend folders (no React or HTML files). However, CORS configurations in `settings.py` indicate that a frontend is expected to run at `http://localhost:3000`.

### Backend
* **Python**: Base programming language (version 3.10+ recommended).
* **Django & Django REST Framework (DRF)**: Powers the main CRUD API, relational modeling, and user authentication.
* **FastAPI & Uvicorn**: Powers the high-performance asynchronous AI Engine.
* **LangGraph (from LangChain)**: Provides the stateful agent orchestration graph inside the AI Engine.
* **ReportLab**: Compiles Case, Accused, and Victim details into downloadable PDFs with layout styling.
* **Psycopg2-binary**: Python PostgreSQL adapter.

### Database
* **PostgreSQL (Neon Cloud)**: Holds the master police relational schema (Lookup tables, State, Rank, Unit, CaseMaster, Accused, Victim, etc.).
* **Neo4j Aura (Cloud Graph)**: Stores Case, Accused, and Witness entities as nodes and maps relationships (`FILED_BY`, `ACCUSED_IN`, `VICTIM_OF`) to discover networks.
* **Qdrant (Cloud Vector DB)**: Contains vectorized summaries/briefs of case facts (`crime_cases` collection) to enable semantic vector lookup.
* **SQLite (Local)**: Used as a fallback local database for development when cloud PostgreSQL environment variables are missing.

### AI / ML Components
* **LLM Client (Ollama / Groq)**: The AI Engine queries LLMs. Configured for local Ollama (`qwen3` model) or cloud Groq APIs using standard `urllib.request`.
* **FastEmbed**: Generates local vector embeddings (`BAAI/bge-small-en-v1.5`, 384 dimensions) for Qdrant indexing.

---

## 4. Complete Project Structure

```
d:\VigilX-BE\
├── backend\
│   ├── requirements.txt         # Dependencies for backend apps
│   ├── .env                     # Shared credentials for PostgreSQL, Neo4j, and Qdrant
│   │
│   ├── django-api\              # Django CRUD & REST API Server
│   │   ├── manage.py            # Django admin command entry point
│   │   ├── django_seed.py       # Seeds mockup cases in Django database
│   │   ├── config\              # Django project configuration (settings.py, urls.py)
│   │   ├── api\                 # API serialization, middleware, and RBAC permissions
│   │   │   ├── serializers\     # Formats data and implements PII redactions
│   │   │   ├── permissions\     # IsSupervisor, IsCaseWriteAuthorized, DenyPolicymakerPII
│   │   │   ├── middleware\      # AuditLogMiddleware and ExceptionHandlingMiddleware
│   │   │   └── urls\            # Configures DRF routers and auth paths
│   │   └── apps\                # Modular Django Apps
│   │       ├── users\           # Custom User Model & roles (Investigator, Supervisor...)
│   │       ├── cases\           # Core FIR, Victim, Accused, and ClueEntity models
│   │       ├── investigation\   # Case diary log models and endpoints
│   │       ├── audit\           # AuditLog models for supervisor tracking
│   │       ├── authentication\  # Login, Refresh, and Logout views (JWT)
│   │       └── reports\         # PDF Generation view (CaseReportView)
│   │
│   ├── ai-engine\               # FastAPI AI Reasoning Service
│   │   ├── main.py              # FastAPI app setup and health endpoint
│   │   ├── requirements.txt     # AI Engine-specific python libraries
│   │   ├── routers\             # API Routes (/ai/ask post router)
│   │   ├── schemas\             # Pydantic schema validation (common, conversation, rest)
│   │   ├── utils\               # Config env readers and custom logging formatters
│   │   ├── prompts\             # System prompt text templates (intent, reasoning, summaries)
│   │   ├── agents\              # LangGraph orchestration state machine (workflow.py)
│   │   ├── neo4j\               # Neo4j Graph DB connection manager
│   │   ├── graph\               # Neo4j Node and Relationship schema mapping & ingestion
│   │   ├── analytics\           # Neo4j Network analyzer (co-accused, syndicates)
│   │   ├── profiling\           # Heuristic suspect profile risk calculator
│   │   ├── forecasting\         # Heuristic forecasting engines
│   │   ├── recommendation\      # Graph-traversal suspect recommendations
│   │   └── services\            # Rest clients, SQL planners, RAG Retrievers
│   │
│   └── database\                # Data population scripts and SQL scripts
│       ├── postgres\            # Relational SQL schema scripts (schema.sql)
│       ├── neo4j\               # Constraints setup script
│       ├── qdrant\              # Vector collection initializer
│       └── seed_all_mock_data.py # Seeds all 3 databases (Neon, Neo4j Aura, Qdrant)
│
├── requirements.txt             # Workspace dependencies (includes fastembed)
└── run_servers.bat              # Script to launch Django (8000) and FastAPI (8001) in parallel
```

---

## 5. Complete Feature Inventory

### A. Authentication & User Management
* **Description**: Secure registration, JWT-based login (TokenObtainPair), token rotating refresh, and user profile retrieval (`/api/users/me/`).
* **RBAC Enforcement**: Registering and list CRUD on `/api/users/` restricted to `SUPERVISOR` role.
* **Status**: *Fully implemented*.
* **Files**: [models.py](file:///d:/VigilX-BE/backend/django-api/apps/users/models.py), [views.py](file:///d:/VigilX-BE/backend/django-api/apps/users/views.py), [serializers/auth.py](file:///d:/VigilX-BE/backend/django-api/api/serializers/auth.py).

### B. First Information Report (FIR) Management
* **Description**: Create, update, view, and list FIR cases. Filter by status, date ranges, and officer ID. Search by keyword across descriptions, victim names, complainant names, and suspect names.
* **RBAC Enforcement**: Read is open to all authenticated users. Write operations (POST, PUT, PATCH, DELETE) are restricted to `SUPERVISOR` and `INVESTIGATOR` roles.
* **Status**: *Partially implemented* (Django models mapping is incomplete, see Section 18).
* **Files**: [models.py](file:///d:/VigilX-BE/backend/django-api/apps/cases/models.py), [views.py](file:///d:/VigilX-BE/backend/django-api/apps/cases/views.py), [serializers/cases.py](file:///d:/VigilX-BE/backend/django-api/api/serializers/cases.py).

### C. Personal Identity (PII) Redaction
* **Description**: Dynamically redacts phone numbers, addresses, statements, and criminal history in serialized case details and reports when the request is made by a `POLICYMAKER`. Completely blocks policymakers from accessing raw victim/accused endpoints directly.
* **Status**: *Fully implemented*.
* **Files**: [rbac.py](file:///d:/VigilX-BE/backend/django-api/api/permissions/rbac.py), [serializers/cases.py](file:///d:/VigilX-BE/backend/django-api/api/serializers/cases.py).

### D. Case Clue Entity Matching
* **Description**: Registers and searches clue items (like phone numbers, vehicles, bank accounts) linked with FIRs to discover shared characteristics across crimes.
* **Status**: *Fully implemented*.
* **Files**: [models.py](file:///d:/VigilX-BE/backend/django-api/apps/cases/models.py#L125), [views.py](file:///d:/VigilX-BE/backend/django-api/apps/cases/views.py#L132).

### E. Case Report Export (PDF Generation)
* **Description**: Generates a formatted PDF containing FIR details, Victim Profiles, Accused Profiles, Clues, and Case Diaries. Respects Policymaker PII redaction by printing `[REDACTED]` where required.
* **Status**: *Fully implemented*.
* **Files**: [views.py](file:///d:/VigilX-BE/backend/django-api/apps/reports/views.py).

### F. Automated Audit Logging
* **Description**: Custom Django middleware automatically intercepts mutating requests (POST, PUT, PATCH, DELETE) and login endpoints, logs them to the `AuditLog` table with user info, actions, IP addresses, and response codes, while sanitizing passwords and secret tokens.
* **Status**: *Fully implemented*.
* **Files**: [audit.py](file:///d:/VigilX-BE/backend/django-api/api/middleware/audit.py), [models.py](file:///d:/VigilX-BE/backend/django-api/apps/audit/models.py).

### G. AI Reasoning Agent (/ai/ask)
* **Description**: A conversational AI endpoint executing a 5-node LangGraph pipeline. It classifies the user's intent, builds a REST API search plan, queries the Django API, fetches semantically similar vector chunks, combines the contexts, verifies evidence thresholds, and runs an LLM to generate cited answers.
* **Status**: *Partially implemented* (FastAPI configuration missing critical REST endpoint variables, see Section 18).
* **Files**: [workflow.py](file:///d:/VigilX-BE/backend/ai-engine/agents/workflow.py), [main.py](file:///d:/VigilX-BE/backend/ai-engine/main.py).

### H. Suspect Recommendation Engine
* **Description**: Backend Cypher queries that traverse Neo4j to find co-accused individuals from previous cases who are associated with the current case's suspects.
* **Status**: *Backend-only / Unused* (No HTTP router exposed in FastAPI).
* **Files**: [engine.py](file:///d:/VigilX-BE/backend/ai-engine/recommendation/engine.py).

### I. Risk Profiling Generator
* **Description**: Computes risk scores and aggregates co-accused networks for a suspect in the graph.
* **Status**: *Backend-only / Unused* (No HTTP router exposed in FastAPI).
* **Files**: [generator.py](file:///d:/VigilX-BE/backend/ai-engine/profiling/generator.py).

### J. Syndicate Network Detection
* **Description**: Finds pairs of suspects who share multiple crime cases, identifying organized syndicates in the Neo4j graph.
* **Status**: *Backend-only / Unused* (No HTTP router exposed in FastAPI).
* **Files**: [network.py](file:///d:/VigilX-BE/backend/ai-engine/analytics/network.py#L43).

---

## 6. User Roles and Permissions

The system defines four roles via `UserRole` choices:

| Role | DRF Case Write | DRF Case Read | Direct PII Access | User Admin | View Audit Trail |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Supervisor** | Yes | Yes | Yes | Yes | Yes |
| **Investigator** | Yes | Yes | Yes | No | No |
| **Crime Analyst** | No | Yes | Yes | No | No |
| **Policymaker** | No | Yes | **No (Redacted)** | No | No |

* **RBAC Implementation**: Enforced at the DRF ViewSet layer using custom permissions:
  * `IsSupervisor`: Restricts user administration.
  * `IsCaseWriteAuthorized`: Limits mutating methods (POST/PUT/PATCH/DELETE) on cases, victims, and accused to Investigators and Supervisors.
  * `DenyPolicymakerPII`: Blocks Policymakers from `/api/victims/` and `/api/accused/`.
  * `to_representation` in case serializers: Dynamically swaps sensitive values for `'[REDACTED]'`.

---

## 7. Complete User Workflows

```
[User Action: Log FIR]
  │
  ▼
[Frontend sends POST request to /api/cases/]
  │
  ▼
[Django REST Framework] ──(Checks IsCaseWriteAuthorized: Only Investigator/Supervisor)
  │
  ▼
[AuditLogMiddleware logs request, sanitizes body] ──(Saves to AuditLog table)
  │
  ▼
[Django ORM writes CaseMaster record to Neon DB/SQLite]
  │
  ▼
[Response 201 HTTP success returned to Client]
```

```
[User Action: Ask AI: "What is John Doe's history?"]
  │
  ▼
[FastAPI /ai/ask endpoint receives request]
  │
  ▼
[AIOrchestrator Workflow]
  ├── 1. Log question in conversation history
  ├── 2. Intent Detection (detects 'case_lookup' or 'suspect_query')
  ├── 3. SQL Planner generates REST search query (RestCapability.CASE_SEARCH)
  ├── 4. REST Client calls Django API (/api/cases/?search=John+Doe) using authorization token
  ├── 5. RAG Retriever queries Vector Database for semantic match (simulated via REST mapping)
  ├── 6. Context Combiner merges RAG text + REST API records
  ├── 7. Evidence Threshold Checker verifies if citations count is met
  └── 8. LLM generator outputs cited, evidence-grounded answer
  │
  ▼
[FastAPI returns StandardResponse containing answer and citations list]
```

---

## 8. System Architecture

```
                       ┌──────────────────────┐
                       │   Client / Frontend  │
                       │ (e.g. localhost:3000)│
                       └──────────┬───────────┘
                                  │
                  ┌───────────────┴───────────────┐
                  ▼                               ▼
      ┌───────────────────────┐       ┌───────────────────────┐
      │   FastAPI AI Engine   │       │   Django REST Server  │
      │   (localhost:8001)    │       │   (localhost:8000)    │
      └───────────┬───────────┘       └───────────┬───────────┘
                  │                               │
                  │ (REST Client Queries API)     │
                  ├───────────────────────────────┤
                  │                               │
                  ▼                               ▼
        ┌───────────────────┐           ┌───────────────────┐
        │    Qdrant Cloud   │           │    Neon Postgres  │
        │    (Vector DB)    │           │   (Relational DB) │
        └───────────────────┘           └───────────────────┘
                  ▲                               ▲
                  │ (Graph Analytics & Traversals)│
                  └───────────────┬───────────────┘
                                  ▼
                        ┌───────────────────┐
                        │    Neo4j Aura     │
                        │    (Graph DB)     │
                        └───────────────────┘
```

---

## 9. Frontend Analysis

* No frontend code exists in the repository. 
* Interactive behaviors, CSS styles, component routing, visual charts, and frontend views are **Unable to confirm from the existing project.**
* However, CORS settings inside Django's `settings.py` identify `http://localhost:3000` and `http://127.0.0.1:3000` as the designated hosts for the user interface.

---

## 10. Backend Analysis

The backend structure uses separate Django and FastAPI instances to separate concerns:

### Django Applications (`backend/django-api/apps`)
1. **`users`**: Manages the custom user model inheriting from `AbstractUser` and maps roles.
2. **`authentication`**: Integrates simplejwt to handle token creation and refresh views.
3. **`cases`**: Houses the database mappings and endpoints for cases, victims, accused, and clues.
4. **`investigation`**: Records journal diaries (`notes`, `recorded_by`) linked to cases.
5. **`audit`**: Captures user actions.
6. **`reports`**: Generates a PDF compilation of the case history using ReportLab.

### FastAPI AI Engine Services (`backend/ai-engine/services`)
* **`IntentService`**: Evaluates conversation history and question to output logical intent labels (e.g., `case_lookup`).
* **`SQLAgentPlanner` / `SQLAgentService`**: Formulate logical queries mapped to REST endpoints rather than issuing raw SQL strings.
* **`RAGRetriever`**: Calls endpoints on the REST gateway to acquire context vectors, translating records into readable strings.
* **`ReasoningService`**: Sends final prompt blocks to the LLM Client.
* **`ConversationService`**: Stores chat histories locally in a JSON file (`conversation_history.json`).

---

## 11. Database Analysis

VigilX uses three databases in production, with SQLite as a development fallback.

### Neon Cloud PostgreSQL Model
Exposed in `backend/database/postgres/schema.sql`:
* `CaseMaster`: The central table mapped to `CaseMasterID`. Integrates foreign keys to lookup tables (`GravityOffenceID`, `CaseStatusID`, `CrimeMinorHeadID`).
* `ComplainantDetails`, `Victim`, `Accused`: Relate to `CaseMaster` via foreign keys.
* `Employee`: Stores investigator assignments.
* `ArrestSurrender`: Tracks arrest logs.

### Neo4j Graph Model
Exposed in `backend/database/neo4j/constraints.cypher`:
* Nodes: `Case` (indexed by case number/status), `Person` (indexed by age), `Accused`, `Victim`, `Witness`.
* Relationships:
  * `(Person)-[:FILED_BY]->(Case)`
  * `(Person)-[:ACCUSED_IN]->(Case)`
  * `(Person)-[:VICTIM_OF]->(Case)`

### Qdrant Vector Model
Exposed in `backend/database/qdrant/init_collections.py`:
* Collection: `crime_cases`
* Vector Size: 384 dimensions (matches `BAAI/bge-small-en-v1.5` BGE embedding size).
* Metric: Cosine similarity.
* Payload: Holds `case_id` and `brief_facts`.

---

## 12. AI/ML Analysis

* **LangGraph Orchestration**: Uses stateful state-graphs containing nodes (`conversation`, `intent`, `retrieve`, `sql`, `reason`) connected in sequence. Fallback to inline calls occurs if `langgraph` package cannot be imported.
* **Intent Classifier**: Maps queries to intents (`case_lookup`, `evidence_summary`, `timeline_query`, `suspect_query`, `victim_query`, `statistics_query`).
* **Confidence Scoring**: Evaluates the citation sources. High confidence requires multiple source hits from at least two source systems (e.g. RAG + API).
* **LLM Client Boundary**: Handles HTTP payload compilation for Groq chat formats or Ollama completion parameters.

---

## 13. Authentication and Security Analysis

* **Token Auth**: Relies on Bearer JWTs via SimpleJWT.
* **Redaction Logic**: Handled on-the-fly during serialization (`to_representation`), ensuring that raw databases are protected at the API level from policymakers.
* **Secret Sanitization**: `AuditLogMiddleware` intercepts logs and replaces occurrences of 'password', 'secret', 'token', and 'refresh' with `'********'`.
* **Security Risk**: `LogoutView` simply returns a success envelope without blacklisting the refresh token on the server side.

---

## 14. API Inventory

### Django REST API (port 8000)

| Endpoint | Method | Auth | Role Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `/api/auth/login/` | POST | None | Any | Returns access/refresh JWT tokens. |
| `/api/auth/refresh/` | POST | None | Any | Rotates access token using a refresh token. |
| `/api/auth/logout/` | POST | Token | Any | Discards tokens (client-side). |
| `/api/users/me/` | GET | Token | Any | Returns current user profile. |
| `/api/users/` | GET/POST | Token | Supervisor | Lists or registers users. |
| `/api/cases/` | GET/POST | Token | Write: Inv/Sup | Lists or registers FIR cases. |
| `/api/cases/<id>/` | GET/PUT/PATCH/DELETE | Token | Write: Inv/Sup | Manages a specific FIR case. |
| `/api/victims/` | GET/POST/PUT/DELETE | Token | Write: Inv/Sup | CRUD on victims (Denies Policymakers). |
| `/api/accused/` | GET/POST/PUT/DELETE | Token | Write: Inv/Sup | CRUD on suspects (Denies Policymakers). |
| `/api/entities/` | GET/POST/PUT/DELETE | Token | Write: Inv/Sup | Registers/queries clues (phone number matches). |
| `/api/investigations/` | GET/POST/PUT/DELETE | Token | Write: Inv/Sup | CRUD on case diary logs. |
| `/api/audit/` | GET | Token | Supervisor | View system action log history. |
| `/api/cases/<id>/report/` | GET | Token | Any | Downloads PDF compiled report. |

### FastAPI AI Engine API (port 8001)

| Endpoint | Method | Auth | Input Body | Description |
| :--- | :--- | :--- | :--- | :--- |
| `/health` | GET | None | None | Checks system status. |
| `/ai/ask` | POST | Token (Optional) | `AskRequest` | Orchestrates RAG, REST queries, and returns cited answers. |

---

## 15. Data Flow Analysis

### Conversational Query Execution Flow
1. User types question $\rightarrow$ Client posts to `/ai/ask` with Bearer JWT.
2. FastAPI intercepts request $\rightarrow$ `AIOrchestrator` starts graph.
3. `conversation` node records question $\rightarrow$ loads recent conversation window.
4. `intent` node calls LLM $\rightarrow$ returns intent category (e.g. `suspect_query`).
5. `retrieve` node calls REST client $\rightarrow$ queries Django endpoints (e.g. `/api/accused/`) using the user's authorization token.
6. `sql` node merges returned fields into text format.
7. `reason` node compares evidence size $\rightarrow$ if below threshold, outputs default "insufficient data" message. If above, passes combined context to LLM.
8. LLM returns formatted answer $\rightarrow$ AI Engine returns response containing markdown text, metadata, and citation objects.

---

## 16. Feature Completion Matrix

| Module / Feature | Implemented | Partially Implemented | Missing | Broken | Status |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Authentication & JWT** | Yes | - | - | - | **Completed** |
| **User Profile Endpoint** | Yes | - | - | - | **Completed** |
| **FIR Case Management** | - | Yes | - | Yes | **Partially Implemented & Broken** (Property mapping model bugs, breaks CRUD tests) |
| **Victim & Accused Profile** | - | Yes | - | Yes | **Partially Implemented & Broken** (Property mapping model bugs, breaks CRUD tests) |
| **PII Dynamic Redaction** | Yes | - | - | - | **Completed** |
| **Case PDF Report Export** | Yes | - | - | - | **Completed** |
| **Audit Logs Middleware** | Yes | - | - | - | **Completed** |
| **AI Orchestrator Engine** | - | Yes | - | Yes | **Partially Implemented & Broken** (Unconfigured Rest endpoints in .env) |
| **Suspect Graph Recommender**| Yes | - | - | - | **Unused Backend Only** (No REST path exposed) |
| **Network Syndicate Finder** | Yes | - | - | - | **Unused Backend Only** (No REST path exposed) |
| **Suspect Risk Profiler** | Yes | - | - | - | **Unused Backend Only** (No REST path exposed) |
| **Graph DB Sync Ingestion** | - | - | Yes | - | **Missing Core Functionality** (No active synchronizer triggers) |

---

## 17. Current Project Development Status

The codebase resides in an **Advanced MVP** stage.
* **Completed Infrastructure**: The foundational modules, custom authentication layers, JWT middleware, audit-logging schemas, and PDF report compilation are functional and production-grade. The three-way database connection parameters (Neon PostgreSQL, Neo4j, Qdrant) are setup and seeded.
* **Unfinished Integration**: The AI Engine's graph-based analytics utilities (profiler, syndicate analyzer, recommender) are written and tested, but lack API gateway routing, meaning they cannot be invoked by a client.
* **Critical Mismatch/Broken Suite**: Django ORM schema constraints are bypassed using hardcoded property descriptors on `FIR`, `Victim`, and `Accused`. Because database columns were omitted from Django models, the model seeding scripts and standard tests fail upon database write.

---

## 18. Technical and Functional Problems

### A. Environment Configuration Mismatch (Django DB)
* **Problem**: In `settings.py`, the PostgreSQL configuration looks for `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, and `DB_PORT`. However, the `.env` file defines database parameters as `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, and `POSTGRES_PORT`.
* **Impact**: Django fails the lookup condition and silently falls back to a local SQLite database (`db.sqlite3`), completely bypassing the cloud Neon PostgreSQL database in normal execution modes.

### B. Environment Path Loading Mismatch
* **Problem**: In Django `settings.py`, the path is resolved via `BASE_DIR.parent.parent / '.env'` (expecting `.env` at the root `d:\VigilX-BE\.env`). In FastAPI `config.py`, it loads `.parent.parent.parent.parent / ".env"` (also expecting root).
* **Impact**: The `.env` file is actually located inside the subfolder `d:\VigilX-BE\backend\.env`. Consequently, neither server will load the configuration file during startup unless it is moved or the paths are corrected.

### C. Django Database Model Property Mismatch (Fatal ORM Bug)
* **Problem**: In `apps/cases/models.py`, fields like `crime_type`, `location`, `latitude`, `longitude`, `status`, and `officer_in_charge` are implemented as Python `@property` methods returning dummy data (e.g. `None` or `CrimeType.THEFT`). They are not actual Django model fields.
* **Impact**: `django_seed.py` and `apps/cases/tests.py` attempt to save data into these fields using `FIR.objects.create(...)` and `Victim.objects.create(...)`. Because properties are read-only and not database fields, these calls throw `TypeError` / `FieldError` exceptions, breaking both the test suite and database seeding.

### D. AI Engine Rest API Gateway Configuration Mismatch
* **Problem**: The AI Engine retrieves data by making internal REST requests. The paths are resolved dynamically via environment variables like `AI_ENGINE_REST_CASE_SEARCH_PATH`.
* **Impact**: None of these variables are defined in the `.env` file. Consequently, the registry returns `None` for endpoint paths, causing all AI requests on `/ai/ask` to fail with `endpoint_not_configured`.

### E. Graph Database Ingestion Gap
* **Problem**: The `CaseExtractor` class is responsible for loading Django records into Neo4j graph nodes. However, this is only used in mock unit tests.
* **Impact**: There are no signals, celery tasks, or API hooks to trigger the extractor when a new FIR is registered. The PostgreSQL database and the Neo4j graph database will immediately fall out of sync.

### F. SimpleJWT Token Blacklist Absence
* **Problem**: SimpleJWT's blacklist features are omitted from `INSTALLED_APPS` and settings.
* **Impact**: A logged-out user's token remains valid until expiry. The logout endpoint simply outputs a success response without blacklisting the token.

---

## 19. Missing Functionality

Based on product goals, the following components are completely missing:
1. **Frontend App**: No dashboard views, case tables, profile views, or AI query interfaces exist in this workspace.
2. **Active Graph Sync Task**: A background worker (e.g., Celery) or Django signal receiver to trigger `CaseExtractor.process_case_payload` when case details change.
3. **Graph Analytics API Endpoints**: REST routers exposing suspect profiling risk indicators, syndicate structures, and proactive leads from the graph database to the client.
4. **Vector Database Sync Ingestion**: A utility to embed and index case descriptions in Qdrant when cases are created.

---

## 20. Project Understanding Summary

VigilX-BE is a dual-service backend system (Django API + FastAPI AI Engine) managing structured and semantic crime records. The Django REST API successfully restricts data views and redacts sensitive PII depending on user roles. The FastAPI AI Engine orchestrates user queries using a structured LangGraph state machine. However, the system is currently unusable in its default state because of critical configuration paths and database model properties that break seeding, database connections, unit tests, and internal API calls. Fixing these model mappings and environment files is required to establish core system functionality.

---
*End of Report.*
