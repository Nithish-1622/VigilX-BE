# Frontend Integration Guide - VigilX Backend APIs & AI Engine

Welcome, Frontend Developer! This guide provides a comprehensive overview of all backend services, authentication mechanisms, database models, and the AI Engine integration endpoints developed so far. Use this to integrate the React/Next.js user interface with the VigilX Crime Intelligence Platform.

---

## 1. System Architecture & Ports

The backend operates as a dual-service architecture. Running the main startup script launches both services simultaneously:

* **Django REST API (Gateway & Database)**: `http://127.0.0.1:8000`
  * Handles authentication, relational databases (PostgreSQL/SQLite), search filters, case records, and PDF report exports.
* **FastAPI AI Engine (Orchestrator)**: `http://127.0.0.1:8001`
  * Runs the multi-agent reasoning loops, intent classification, memory management, and communicates with the **Groq Cloud LLM** (Llama-3.3-70b).

---

## 2. Authentication Flow (JWT)

All database and AI endpoints (except login) require a valid JWT access token in the request headers:
`Authorization: Bearer <access_token>`

### A. Login Endpoint
* **Endpoint**: `POST http://127.0.0.1:8000/api/auth/login/`
* **Content-Type**: `application/json`
* **Request Body**:
  ```json
  {
    "username": "officer1",
    "password": "Officer123!"
  }
  ```
* **Response Body**:
  ```json
  {
    "refresh": "eyJhbGciOiJIUzI1NiIsIn...",
    "access": "eyJhbGciOiJIUzI1NiIsIn..."
  }
  ```

### B. Refresh Token
* **Endpoint**: `POST http://127.0.0.1:8000/api/auth/refresh/`
* **Request Body**:
  ```json
  {
    "refresh": "<your_refresh_token>"
  }
  ```

---

## 3. Core Database Endpoints (Django)

All list endpoints are paginated and return records in standard Django REST Framework wrappers.

### A. FIR Cases
* **List Cases**: `GET /api/cases/`
  * **Optional Parameters**:
    * `?search=FIR-123` (filters cases matching FIR number or description keywords)
* **Create Case**: `POST /api/cases/`
  ```json
  {
    "fir_number": "FIR-456",
    "crime_type": "BURGLARY",
    "incident_date_time": "2026-07-14T10:00:00Z",
    "reported_date_time": "2026-07-14T11:30:00Z",
    "location": "Indiranagar, Bengaluru",
    "latitude": 12.9716,
    "longitude": 77.6412,
    "status": "PENDING",
    "description": "Burglary reported at electronic warehouse store."
  }
  ```
* **Get Case Details**: `GET /api/cases/<id_uuid>/`

### B. Accused / Suspects Profiles
* **List Accused**: `GET /api/accused/`
  * **Optional Filters**:
    * `?fir=<fir_uuid>` (returns suspects only linked to a specific case ID)

### C. Victims Profiles
* **List Victims**: `GET /api/victims/`
  * **Optional Filters**:
    * `?fir=<fir_uuid>`

### D. Investigation Logs (Diary entries)
* **List Logs**: `GET /api/investigations/`
* **Add Log Entry**: `POST /api/investigations/`
  ```json
  {
    "fir": "<fir_uuid>",
    "activity_summary": "Searched suspect's prior residence.",
    "activity_details": "No physical clues retrieved at Indiranagar house.",
    "date_time": "2026-07-14T14:00:00Z"
  }
  ```

---

## 4. Conversational AI Orchestrator (FastAPI)

Use this endpoint to power the **Crime Assistant chatbot**. It maintains multi-turn conversation memory, resolves pronouns, queries the backend automatically, and generates cited reasoning summaries.

* **Endpoint**: `POST http://127.0.0.1:8001/ai/ask`
* **Headers**:
  * `Authorization: Bearer <access_token>`
  * `Content-Type`: `application/json`
* **Request Body**:
  ```json
  {
    "session_id": "chatbot-session-101",
    "user_id": "officer-john-1",
    "question": "Where does John Doe live?"
  }
  ```
* **Response Body**:
  ```json
  {
    "success": true,
    "message": "ok",
    "data": {
      "answer": "John Doe lives at No. 5, 2nd Cross, Koramangala.",
      "intent": "suspect_query",
      "summary": "user: Where does John Doe live?",
      "case_summary": null,
      "evidence_used": 2
    },
    "metadata": {
      "intent": "suspect_query",
      "evidence_sources": 2,
      "api_records": 1,
      "langgraph_enabled": true,
      "confidence": "medium",
      "evidence_threshold_met": true,
      "rag_citations": 1,
      "sql_citations": 1,
      "evidence_source_breakdown": {
        "accused_records": 1,
        "django_api": 1
      }
    },
    "citations": [
      {
        "source": "accused_records",
        "reference_id": "b20363f3-6346-4c04-a358-9dfa2614f68b",
        "snippet": "id=b20363f3-6346-4c04-a358-9dfa2614f68b; name=John Doe; address=No. 5, 2nd Cross, Koramangala; ...",
        "score": null
      }
    ],
    "errors": null
  }
  ```

### Key Chatbot UI Features:
1. **Interactive Citations**: The `citations` array contains snippets of the exact records from which the AI answered. You can render these as clickable badges/cards below the chatbot message to allow officers to inspect raw source records.
2. **Session Persistence**: Keep `session_id` persistent for a specific chatbot tab session to let the AI engine maintain reference memory (e.g. knowing `"he"` refers to John Doe in subsequent questions).
3. **Intent Detection**: The `intent` field informs the UI about the detected topic (e.g. `timeline_query`, `suspect_query`, `statistics_query`), allowing you to dynamically adapt UI layouts or highlight matching components.
