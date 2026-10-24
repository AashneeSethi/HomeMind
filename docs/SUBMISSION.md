# HomeMind — Hackathon Submission Kit 🏆

> **Submission Document**: Amazon Build, Ship, Shape Hackathon  
> **Project Name**: HomeMind  
> **Tagline**: Context-Aware Multi-Device AI Home Agent  
> **Core Concept**: Ambient decision & context layer for Alexa+, Ring, and Fire TV.

---

## 1. Hackathon Submission Form Content

### Project Title
**HomeMind: Context-Aware Multi-Device AI Home Agent**

### Elevator Pitch (1-2 Sentences)
HomeMind is an intelligent context, memory, and decision layer that transforms smart home devices from noisy, isolated trigger scripts into a unified ambient presence. By reasoning over occupancy modes, active monitoring intentions, and attention thresholds, HomeMind determines what happened, whether it matters, and which device (Alexa voice or Fire TV screen) should communicate it.

### The Problem It Solves
Current smart homes suffer from severe notification fatigue and lack situational awareness. A perimeter motion sensor, doorbell ring, or patio camera will fire indiscriminately, interrupting dinner or work focus with identical chime sounds. Devices operate as disjointed silos: Ring detects, Alexa announces, and Fire TV streams, but none understand what the household is currently doing.

### Core Differentiator
The key differentiator is **contextual decision intelligence**, not simple API bridging:
1. **Context-Aware Attention Management**: Distinguishes between routine ambient motion and actionable events based on occupancy mode (`home`, `away`, `sleep`, `focus`).
2. **Intent-Driven Temporary Watches**: Users can establish conversational monitoring intentions (e.g. *"Watch the front door for 30 minutes"*), dynamically adjusting significance thresholds.
3. **Multimodal Routing**: Intelligently routes notifications to the appropriate interface—suppressing intrusive audio in focus mode in favor of subtle visual context cards on Fire TV.
4. **Standards-Compliant MCP Architecture**: Implements 6 Model Context Protocol tools ready to be exposed to Alexa+ as Agent Skills over Streamable HTTP.

### Amazon Technologies Utilized & Architecture Role

| Amazon Technology | Hackathon Implementation Role | Production Roadmap |
| :--- | :--- | :--- |
| **Alexa+ / Echo** | Modeled via standards-compliant Model Context Protocol (MCP) server & simulated conversational interface. | Exposing MCP server over Streamable HTTP as native Alexa+ Agent Skills. |
| **Ring** | Event ingestion pipeline modeling real-world doorbell chimes, perimeter motion, and door contact events. | Direct webhook integration with HMAC-SHA256 signature verification. |
| **Fire TV** | Ambient visual dashboard modeling picture-in-picture banners and quiet context cards. | Dedicated React/Android TV client receiving WebSocket push updates. |
| **AWS** | Architecture designed for cloud-native deployment. | AWS App Runner / ECS containerization, DynamoDB state persistence, and Amazon Bedrock reasoning. |

### Technical Stack Built
- **Backend**: Python 3.11+, FastAPI, Pydantic v2, Uvicorn, Model Context Protocol Python SDK.
- **Frontend / UI**: React 18, Vite, Lucide React, Modern Dark Mode Control Center.
- **Testing**: Pytest test suite with 28 automated unit and integration tests (100% passing).

### Honest Implementation Boundaries
- **Ring Ingestion**: Implemented through standardized event endpoints (`POST /events` and `POST /simulate/event`) rather than live Ring cloud OAuth webhooks.
- **Alexa+ Integration**: Implemented via a fully compliant local MCP server and deterministic conversational agent matching Alexa+ Agent Skill specifications.
- **State Storage**: Implemented in high-performance in-memory working models (`ContextManager` & `MemoryManager`), architected for straightforward DynamoDB persistence.
- **Device Hardware**: Hardware dispatchers use abstracted provider interfaces (`BaseIntegration`), logging simulated multimodal delivery.

---

## 2. 2-Minute Video Demo Script

**Total Duration**: 2 minutes (120 seconds)  
**Presenter Setup**: Browser window open to `http://localhost:5173` with backend running on port 8081.

| Time | On-Screen Action | Spoken Narration |
| :---: | :--- | :--- |
| **0:00 - 0:25** | Start on HomeMind Control Center. Point mouse to Header, Home State card, and Connection badge (`Backend Online (Port 8081)`). | *"Hello! This is HomeMind — an intelligent, context-aware multi-device home agent built for the Amazon Build, Ship, Shape Hackathon. Today's smart homes suffer from notification fatigue. Every camera chime or sensor flutter interrupts you, regardless of what you are doing. HomeMind solves this by acting as the central brain across Ring, Alexa, and Fire TV — deciding what happened, whether it matters, and which device should communicate it."* |
| **0:25 - 0:55** | Scroll to the **HomeMind Conversation Panel**. Type: <br>`Watch the front door for 30 minutes.`<br>Press **Send**. Highlight the newly created card under **Active Watches**. | *"HomeMind implements the Model Context Protocol, meaning it can expose native tools directly to Alexa+ as Agent Skills. Watch what happens when I tell Alexa: 'Watch the front door for 30 minutes.' HomeMind executes the `set_temporary_watch` MCP tool. Notice how the dashboard immediately establishes an active watch for the front door with an active countdown timer."* |
| **0:55 - 1:25** | 1. Click **Simulate Doorbell** under Simulation Controls. Point to the new alert.<br>2. Click **Set Focus Mode**.<br>3. Click **Simulate Motion**. | *"Now let's simulate a real-world Ring event. When someone presses the doorbell, HomeMind recognizes that this matches our active watch, escalating an immediate multimodal alert. But what happens when the user is working? Let's switch to 'Focus Mode'. When motion is detected in Focus mode, HomeMind's Decision Engine suppresses loud audible interruptions, updating our ambient context silently while preserving the alert history."* |
| **1:25 - 1:45** | Return to the Conversation Panel. Type:<br>`What happened at the front door?`<br>Press **Send**. Highlight the synthesized reply. | *"Later, when you want to catch up, you don't need to scroll through video clips. You simply ask Alexa+: 'What happened at the front door?' HomeMind invokes the `what_happened` MCP tool, querying short-term memory and synthesizing a clear natural-language summary of recent activity."* |
| **1:45 - 2:00** | Switch view to architecture diagram or terminal showing `pytest` (28 passed) and conclude. | *"HomeMind features a fully tested Python FastAPI backend, 6 standard MCP tools, and a live React control center. By decoupling perception, context, and multi-device routing, HomeMind delivers true ambient intelligence. Thank you!"* |

---

## 3. Submission Evidence & Screenshot Checklist

Capture the following screenshots and verify each before finalizing your submission upload:

- [ ] **Screenshot 1: Home State & Ambient Context Overview**
  - **URL / Screen**: `http://localhost:5173`
  - **Capture Area**: Header, Connection Badge, and Home State metrics.
  - **Key Highlight**: Demonstrates live connection to port 8081, active occupancy mode, device inventory count, and context summary.
- [ ] **Screenshot 2: Intent-Driven Active Watch with Countdown**
  - **URL / Screen**: `http://localhost:5173` (Active Watches section).
  - **Capture Area**: The active watch card showing `front_door`, remaining duration, and cancel button.
  - **Key Highlight**: Demonstrates conversational memory management triggered via MCP.
- [ ] **Screenshot 3: Ring Event Ingestion & Alert Escalation**
  - **URL / Screen**: `http://localhost:5173` (Active Alerts & Recent Events).
  - **Capture Area**: Alert banner showing `doorbell_press` event at `front_door` with timestamp and Dismiss button.
  - **Key Highlight**: Demonstrates the 5-step cognitive pipeline translating sensor input into actionable alerts.
- [ ] **Screenshot 4: Alexa+ Conversational Panel with MCP Tool Call**
  - **URL / Screen**: `http://localhost:5173` (HomeMind Conversation Panel).
  - **Capture Area**: Chat thread showing user utterance (`What happened at the front door?`) and HomeMind's structured synthesized answer.
  - **Key Highlight**: Demonstrates two-way agentic interaction through the Model Context Protocol.
- [ ] **Screenshot 5: Backend Automated Test Suite Execution**
  - **Capture Area**: Terminal executing `python -m pytest -v`.
  - **Key Highlight**: Clean terminal output showing **28 passed in <5s** across agent, memory, decision, MCP, and API test suites.
- [ ] **Screenshot 6: Frontend Production Build Success**
  - **Capture Area**: Terminal executing `npm run build` in `frontend/`.
  - **Key Highlight**: Output verifying Vite production bundle generation (`dist/index.html`, assets) with zero lint or build errors.

---

## 4. Submission Checklist

- [x] Backend test suite verified passing (28/28 tests).
- [x] Frontend production build verified (`dist/` generated cleanly).
- [x] `.gitignore` verified excluding `.venv`, `node_modules`, `dist/`, `.env`, and logs.
- [x] Verified zero hardcoded credentials, access keys, or secrets committed.
- [x] README and architecture documentation updated with exact ports (8081 & 5173).
- [x] Honest limitations clearly stated in submission write-up.
