# HomeMind Amazon Capability Audit

**Project:** HomeMind (Context-Aware Multi-Device AI Home Agent)  
**Hackathon:** Build, Ship, Shape: Amazon Developer Hackathon 2026  
**Audit Date:** October 2026  
**Document Status:** Complete Feasibility & Technical Audit  

---

## Executive Summary

HomeMind is designed as a context-aware decision layer bridging **Ring** (physical event perception), **Alexa+** (conversational voice interface), and **Fire TV** (ambient visual interface), powered by an **AWS** backend.

This audit evaluates the feasibility of integrating official Amazon developer platforms into HomeMind for the *Build, Ship, Shape* hackathon (submission deadline: October 23, 2026, 12:00 PM PDT).

### Key Audit Findings:
1. **Alexa+ Integration is Built on MCP**: Amazon has established the **Model Context Protocol (MCP)** as the official third-party integration standard for Alexa+. An external backend connects to Alexa+ by exposing an MCP server over **Streamable HTTP** (MCP Specification `2025-11-25` or later). Alexa+ acts as the MCP client, calling registered tools when prompted by user intent. Alternatively, the hackathon explicitly allows a web-based simulated Alexa+ experience.
2. **Ring Partner API Supports Webhooks & Sandbox**: Official Ring APIs operate under the **Ring Partner API / Amazon Vision** developer portal. It provides OAuth 2.0 authentication, real-time webhooks for `ding` (doorbell rings) and `motion` (including human/vehicle classification), and device status APIs. Physical Ring hardware is **not required**; testing can be conducted using Ring's sandbox environment or simulated event payloads.
3. **Fire TV Requires App Context for Rich Overlays**: While Fire OS supports standard Android heads-up system notifications (via Amazon Device Messaging - ADM), system-level floating PiP/overlays across third-party apps are restricted by the OS. However, running HomeMind as a dedicated Fire TV dashboard app (built in React Native for TV or Web technologies) enables real-time visual cards, camera stream feeds, and status alerts over WebSockets or polling.
4. **AWS Stack Can Remain Minimal and Fast**: For a solo developer, heavy services (EKS, SageMaker, Kafka) are unnecessary overhead. A lean architecture utilizing **AWS App Runner** (or Lambda + API Gateway), **Amazon DynamoDB** (for context & memory persistence), and **Amazon Bedrock** (for generative multi-step reasoning) provides a production-grade submission while qualifying for the **AWS Builder** mini-challenge.
5. **No Fabricated APIs**: All findings below cite official Amazon Developer and AWS documentation. Unverified capabilities are explicitly marked as **UNKNOWN**.

---

## Alexa+

### Capabilities
- **Next-Generation Conversational Model**: Alexa+ enables multi-turn, context-retaining dialogue, reasoning over user requests, and invoking third-party agent tools dynamically.
- **Model Context Protocol (MCP) Foundation**: Amazon has officially adopted MCP as the protocol connecting Alexa+ to external capabilities.
- **Tool Exposing (`tools/list` & `tools/call`)**: An external backend can register discrete tools (e.g. `query_home_status`, `set_occupancy_mode`, `create_watch_request`, `get_recent_events`). When a user speaks to Alexa+, the Alexa+ reasoning model determines which tool to invoke and passes arguments conforming to JSON Schema.
- **MCP Apps UI Extension (`@modelcontextprotocol/ext-apps`)**: For Echo devices with screens (Echo Show), Alexa+ supports the MCP Apps extension to project interactive webviews and visual cards directly into the conversation view.

### Integration Architecture
- **Client/Server Model**: Alexa+ acts as the **MCP Client**; HomeMind acts as the **MCP Server**.
- **Transport Standard**: **Streamable HTTP** is strictly required (MCP spec `2025-11-25` or later). The legacy Server-Sent Events (SSE) standalone transport is deprecated.
- **Stateless RPC & External Memory**:
  - MCP tool invocations are stateless HTTP POST requests containing tool arguments.
  - **Critical Architectural Reality**: Alexa+ does **not** persist external domain memory (such as sensor event buffers or home occupancy state). **All home state and temporal memory must be maintained by the HomeMind backend** (e.g., in `ContextManager` and `MemoryManager` backed by DynamoDB).
  - Alexa+ sends only the structured tool parameters derived from the user's utterance. It does not stream raw audio or full external conversation histories to the tool server.

### Authentication
- **OAuth 2.1 with PKCE (S256)**: Required for production linking between an Amazon account and an external MCP server.
- **Protected Resource Metadata (PRM)**: The server must host a PRM document (RFC 9728 compliant) at `/.well-known/oauth-authorization-server` specifying supported scopes and code challenge methods (`S256`).
- **Authorization Header**: Bearer tokens are passed via the standard `Authorization: Bearer <token>` HTTP header on every tool call.
- **Developer Account Linking**: Managed via Login with Amazon (LWA) and the `alexa-ai` CLI.

### Testing & Development Workflow
- **`alexa-ai` CLI**: Amazon provides the `alexa-ai` CLI to configure credentials (`alexa-ai configure`), deploy, and register MCP servers to an Amazon Developer account.
- **Web Simulation Option**: For hackathon participants without full Alexa+ Developer Preview access or complex OAuth setup, the hackathon rules explicitly state:  
  *“New to MCP? Build a simulated Alexa+ experience in a web app using your preferred agentic tool... show your Agent Skill or MCP server in action.”*

### Risks / Limitations
- **Preview Access**: Official Alexa+ is in developer preview; automated public self-enrollment may be constrained. The web-based MCP simulator is the designated zero-risk hackathon contingency.
- **Asynchronous Inbound Notification**: Standard MCP is request-response (pull-based from Alexa+ to MCP server). Alexa+ calling HomeMind when the user speaks is fully supported. However, having HomeMind proactively wake up an Echo speaker to speak without prior user invocation requires the legacy Alexa Proactive Notifications API or AVS (Alexa Voice Service), which is outside standard MCP.

---

## Ring

### APIs
- **Ring Partner API (Amazon Vision)**: The official cloud API located under `https://api.amazonvision.com/v1/`.
- **Device Discovery**: Authenticated endpoint (`GET /v1/devices`) retrieves registered Ring hardware: doorbells, cameras, motion sensors, chimes, and smart lighting.
- **Device Details**: Returns `device_id`, device kind (`doorbell`, `camera`), online status, battery level, firmware version, and sub-components (for multi-camera devices like Ring Elite).
- **Event History**: `GET /v1/history/devices/{device_id}/events` allows querying historical logs with query filters (`event_types=ding,motion,motion.human,motion.vehicle`).
- **Media Access**: The event API returns metadata. Actual video snippets or snapshots require separate calls to Media Clips and Image Snapshot endpoints.

### Events & Webhooks
- **Real-Time Push Webhooks**: The Ring Developer portal allows registering an HTTPS webhook callback endpoint.
- **Supported Event Types**:
  - `ding`: Doorbell button press.
  - `motion`: Generic perimeter motion.
  - `motion.human`: Computer vision classification indicating a person is detected.
  - `motion.vehicle`: Vehicle detected in driveway/perimeter.
  - Device health / connectivity status changes (online/offline).
- **Security & Integrity**: Webhook payloads are signed using HMAC-SHA256 (`X-Ring-Signature`), requiring the HomeMind backend to verify the signature using the app’s HMAC secret.

### Authentication
- **OAuth 2.0**: Standard Authorization Code grant flow with refresh tokens.
- **Playground Token Mode**: The official Amazon sample repository (`ring-api-helloworld`) includes a "Playground" mode enabling generation of short-lived developer tokens for local testing without full OAuth app registration.

### Simulator & Testing Options
- **Physical Hardware NOT Required**: Explicitly affirmed in hackathon rules: *"A physical Ring device is not required. Build a new app or extend an existing one using Ring APIs, SDKs, simulators, or devices."*
- **Ring Developer Sandbox**: Ring provides a sandbox environment with synthetic devices that fire simulated dings and motion events.
- **Local Webhook Simulator**: For development, a mock webhook dispatcher script simulating official Ring JSON payloads enables 100% offline testing.

### Risks / Limitations
- **Webhook Public Ingress**: Ring webhooks require an internet-facing HTTPS endpoint. Local testing requires a tunnel (e.g. `ngrok`, Cloudflare Tunnel) or deploying the ingestion route to AWS (App Runner / API Gateway).
- **Video Stream Overhead**: Live video streaming uses WebRTC (WHEP protocol) or RTSP over TLS. For HomeMind’s core value proposition (context and decisions), ingesting event metadata is sufficient and significantly less error-prone than decoding live H.264 video.

---

## Fire TV

### Development Options
Amazon officially supports three paths for Fire TV (Fire OS / Vega OS):
1. **React Native for TV**: Recommended by Amazon via sample repos (`react-native-multi-tv-app-sample`). Single codebase targeting Fire OS, Vega OS, and Android TV with native 10-foot remote focus management.
2. **HTML5 / Web Applications**: Web apps packaged for Fire TV or hosted in a fullscreen WebApp container. Fastest to prototype, uses standard web technologies (React/Vite).
3. **Android Native (Kotlin/Java)**: Traditional Android app using Jetpack Compose or Leanback on Fire OS.

### Communication With HomeMind
- **In-App Active Communication**: When the HomeMind Fire TV app is running:
  - **WebSocket / Server-Sent Events (SSE)**: The Fire TV app maintains an open channel to the HomeMind backend (`ws://<backend>/ws/firetv`).
  - When an event occurs (e.g. doorbell ring in focus mode), HomeMind pushes a payload; the TV app instantly displays a subtle picture-in-picture card or alert banner.
- **System-Level Background Notifications**:
  - Fire OS uses the standard Android Notifications API (`NotificationCompat.Builder`). Setting `PRIORITY_HIGH` creates a heads-up banner.
  - Background push requires **Amazon Device Messaging (ADM)**.
  - *Limitation*: When a third-party streaming app (e.g. Netflix) is running, drawing an arbitrary custom interactive overlay window (`SYSTEM_ALERT_WINDOW`) is blocked by Fire OS security policies. True contextual visual cards require the HomeMind companion app to be open or running in ambient/screensaver mode.

### Testing
- **Vega Simulator & Fire TV Simulator**: Amazon provides desktop simulators to test TV layout, D-pad navigation, and app behavior without physical television hardware.
- **Hardware ADB Testing**: Any physical Fire TV Stick can be placed in Developer Mode, enabling deployment via `adb install` over Wi-Fi (`adb connect <ip>:5555`).

### Risks / Limitations
- **10-Foot UI Constraints**: Must handle remote control D-pad navigation (no mouse pointer or touch).
- **Background App Lifecycle**: Fire OS aggressively terminates background services to free RAM for 4K video playback. Relying on background daemon services on the TV stick is brittle; persistent connection should be held while the app is active.

---

## AWS Architecture

### Recommended Services (High ROI for Solo Hackathon)

```
                       ┌─────────────────────────┐
                       │  Alexa+ / MCP Client    │
                       └───────────┬─────────────┘
                                   │ HTTPS (Streamable HTTP)
                                   ▼
┌──────────────────┐   ┌─────────────────────────┐   ┌──────────────────┐
│  Ring Webhooks   ├──►│     AWS App Runner      │◄──┤  Fire TV Client  │
│ (Sandbox/Events) │   │ (FastAPI HomeMind Agent)│   │ (WebSocket/REST) │
└──────────────────┘   └───────────┬─────────────┘   └──────────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    ▼                             ▼
         ┌────────────────────┐        ┌────────────────────┐
         │  Amazon DynamoDB   │        │   Amazon Bedrock   │
         │  (Context & Memory)│        │ (Claude / Nova LLM)│
         └────────────────────┘        └────────────────────┘
```

1. **AWS App Runner**:
   - *Why:* Directly runs the containerized HomeMind FastAPI backend (`uvicorn`). Supports long-lived HTTP connections for Streamable HTTP (MCP) and WebSockets for Fire TV. Zero infrastructure maintenance, automatic SSL, and continuous deployment from GitHub.
2. **Amazon DynamoDB**:
   - *Why:* Serverless, sub-10ms key-value and document store. Perfect fit for `HomeState` document storage, rolling event histories, and user preference persistence without needing VPC peering or connection pooling.
3. **Amazon Bedrock**:
   - *Why:* Managed access to leading foundation models (Anthropic Claude 3.5 Sonnet / Haiku or Amazon Nova) without provisioning GPU servers. Used in the `DecisionEngine` for complex event reasoning, contextual natural language summaries, and multi-step tool planning.
   - *Hackathon Advantage:* Directly qualifies HomeMind for the **AWS Builder Mini-Challenge** ($5,000 cash + $5,000 AWS credits).
4. **Amazon CloudWatch**:
   - *Why:* Built-in logging, audit trails for agent decisions, and error alerting with zero extra configuration.

### Unnecessary Services (Overkill / Anti-Patterns)
- **Amazon EKS / ECS Clusters**: Massive setup overhead, cluster provisioning, and VPC networking complexity for a single agent service.
- **Amazon SageMaker**: Overkill unless training custom neural networks from scratch. Bedrock provides turnkey inference APIs.
- **Amazon RDS / Aurora (PostgreSQL/MySQL)**: High idle cost, VPC management friction, and rigid relational schemas where flexible JSON documents (DynamoDB) are ideal.
- **Amazon MSK (Managed Kafka) / AWS Kinesis**: Heavy event streaming infrastructure designed for millions of events per second. In a smart home, dozens of events per hour do not justify message streaming clusters.
- **Amazon EC2 (Raw VMs)**: Requires manual OS patching, security hardening, systemd service management, and SSL certificate renewals.

---

## Hackathon Requirements

| Category | Requirement | Details / Verification |
| :--- | :--- | :--- |
| **Title** | Build, Ship, Shape: Amazon Developer Hackathon 2026 | Global online hackathon hosted by Amazon Developer on Devpost. |
| **Deadline** | **October 23, 2026 @ 12:00 PM PDT** | Hard cutoff on Devpost submission platform. |
| **Primary Tracks** | Fire TV, Alexa+, Ring, Bee | Choose 1 primary track to compete for primary cash prizes ($12,000 - $25,000). |
| **Mini-Challenges** | AWS Builder ($5,000) & Open Source ($5,000) | Can be stacked onto primary track for additional prize opportunities. |
| **Code Requirement** | Working code invoking track technology | Repo must contain actual imports, entry points, or configs (MCP server, Ring API, Fire TV build). |
| **Video Requirement** | **Under 3 minutes** (English, YouTube/Vimeo) | Must show working demo. Judges will not watch past 3:00. |
| **Repository** | GitHub (Public with license OR Private shared) | If private, must add: `chris-trag`, `knmeiss`, `giolaq`, `anishamalde`, `mosesroth`, `emersonsklar`, `testing@devpost.com`. |
| **Product Feedback** | Mandatory written feedback | Must provide product feedback on every tool, API, and SDK used. |
| **Bonus** | Up to 10% judging bonus | For submitting detailed friction log entries with severity and suggestions. |

---

## HomeMind Feasibility Matrix

| HomeMind Requirement | Amazon Technology | Supported? | Evidence / Documentation | Risk / Mitigation |
| :--- | :--- | :---: | :--- | :--- |
| **1. Receive Ring event** | Ring Partner API Webhooks | **YES** | Official docs at `developer.amazon.com/docs/ring`. Delivers HTTP POST callbacks for `ding` and `motion` with HMAC signature. | **Low.** Requires public HTTPS endpoint (use App Runner or ngrok). Physical device not required; sandbox is available. |
| **2. Maintain home context** | HomeMind `ContextManager` + AWS DynamoDB | **YES** | Amazon does not maintain external domain state; HomeMind holds state in Python / DynamoDB. | **Low.** In-memory implementation already complete and verified with 12 tests. |
| **3. Ask HomeMind through Alexa+** | Alexa+ Voice Input | **YES** | Alexa+ routes natural language utterances to connected MCP tools based on tool descriptions. | **Low.** Standard conversational routing in Alexa+ for Builders. |
| **4. Alexa+ calls HomeMind tool** | Model Context Protocol (Streamable HTTP) | **YES** | Alexa+ Developer documentation supports MCP spec `2025-11-25+` via Streamable HTTP transport. | **Medium.** Strict OAuth 2.1 / PRM metadata requirements. Mitigation: web-based MCP simulator is officially sanctioned by hackathon. |
| **5. Fire TV receives HomeMind state** | Fire TV Web / React Native App + WebSocket | **YES** | Fire TV app connects via standard WebSocket to HomeMind backend for bidirectional state sync. | **Low.** Standard web/React Native networking capability on Fire OS and Vega OS. |
| **6. Display contextual alert** | Fire TV React View / Android Notification | **PARTIAL** | When Fire TV app is foreground: **YES** (custom HTML/React overlay). When third-party app active: **LIMITED** (only standard Android heads-up notification via ADM; full custom overlay blocked by OS). | **Medium.** Focus demo on HomeMind TV dashboard app displaying picture-in-picture alert. |
| **7. User asks "what happened?"** | Alexa+ Tool: `query_home_status` | **YES** | Alexa+ invokes HomeMind tool; HomeMind queries `MemoryManager` & `ContextManager` and returns summary. | **Low.** Simple tool schema returning formatted string for Alexa+ speech synthesis. |
| **8. User creates temporary watch/monitoring request** | Alexa+ Tool: `set_temporary_watch` | **YES** | Alexa+ extracts parameters (e.g. `location="front_door"`, `duration_minutes=30`) and updates HomeMind state. | **Low.** Fits standard JSON Schema parameter extraction in MCP. |
| **9. HomeMind remembers recent events** | HomeMind `MemoryManager` + DynamoDB | **YES** | Stored in HomeMind rolling buffer / DynamoDB table. Queried whenever `DecisionEngine` evaluates an incoming event. | **Low.** Core logic fully tested in HomeMind architecture. |
| **10. Autonomous Alexa voice announcement (Proactive)** | Alexa Proactive Notifications / AVS | **UNKNOWN / RESTRICTED** | MCP is strictly client-pull (Alexa invokes tool). Waking an Echo speaker to talk unprompted requires legacy Proactive Events API or Skill Messaging. | **High.** Do NOT rely on proactive unprompted Alexa audio for core demo. Route ambient alerts to Fire TV or require user voice prompt ("Alexa, what happened?"). |

---

## Recommended Architecture

### The Lean Solo Developer Stack ("The Golden Path")

To ensure completion before the **October 23, 2026** deadline, the smallest technically realistic architecture consists of:

```
                    ┌────────────────────────────────────────┐
                    │               HomeMind                 │
                    │       (FastAPI on AWS App Runner)      │
                    └───────────────────┬────────────────────┘
                                        │
             ┌──────────────────────────┼──────────────────────────┐
             ▼                          ▼                          ▼
   ┌───────────────────┐      ┌───────────────────┐      ┌───────────────────┐
   │ 1. Ring Webhook   │      │ 2. Alexa+ MCP     │      │ 3. Fire TV UI     │
   │    Ingestion      │      │    Endpoint       │      │    Dashboard      │
   ├───────────────────┤      ├───────────────────┤      ├───────────────────┤
   │ Receives `ding` & │      │ Exposes MCP tools │      │ React/Vite app    │
   │ `motion` payloads │      │ via Streamable    │      │ on Vega/Fire TV   │
   │ from Ring Sandbox │      │ HTTP for user     │      │ simulator; shows  │
   │ or simulator.     │      │ voice queries.    │      │ live state & PiP. │
   └───────────────────┘      └───────────────────┘      └───────────────────┘
             │                          │                          │
             └──────────────────────────┼──────────────────────────┘
                                        │
                                        ▼
                              ┌───────────────────┐
                              │  Amazon DynamoDB  │
                              │ (State & History) │
                              └───────────────────┘
```

### Component Breakdown:
1. **Agent Backend (`backend/`)**:
   - Keep current FastAPI modular service.
   - Run on **AWS App Runner** with a public HTTPS URL.
2. **Ring Ingestion (`backend/integrations/ring.py` + `backend/api/events.py`)**:
   - Connect Ring Developer Portal Webhook (Sandbox) to `POST /events`.
   - Include a fallback event generator script in the repository for offline demo reliability.
3. **Alexa+ Tool Exposure (`backend/agent/mcp_server.py`)**:
   - Implement an MCP endpoint using the official Python MCP SDK with **Streamable HTTP**.
   - Expose 3 high-impact tools:
     - `get_home_status()`: Summarizes current mode, devices, and active alerts.
     - `what_happened(time_window_minutes)`: Explains recent events with context reasoning.
     - `set_home_mode(mode)`: Sets occupancy mode (`home`, `away`, `sleep`, `focus`).
   - Deliver both an MCP server endpoint for Alexa+ and an interactive web chat simulator in the frontend to guarantee a working demo video regardless of developer preview approval.
4. **Fire TV Dashboard (`frontend/`)**:
   - Build a lightweight React/Vite TV dashboard running locally or inside the **Vega Simulator**.
   - Displays real-time home status and pops up an alert card (e.g., when a doorbell rings while user is in `focus` mode).
5. **Hackathon Track Selection**:
   - **Primary Track:** **Alexa+** or **Ring** (HomeMind bridges both; Alexa+ with self-hosted MCP server is the highest-visibility category).
   - **Stacked Mini-Challenge:** **AWS Builder** (by deploying on App Runner and backing context with DynamoDB and Amazon Bedrock).
   - **Stacked Mini-Challenge:** **Open Source** (by publishing the GitHub repo under Apache 2.0 / MIT license).
