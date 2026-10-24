# HomeMind Hackathon Submission & Video Checklist 🏆

> **Hackathon**: Amazon Build, Ship, Shape Hackathon (Devpost)  
> **Project Name**: HomeMind  
> **Tagline**: Context-Aware Multi-Device AI Home Agent  
> **Target Video Length**: Under 120 Seconds (Achieved: 111.87 Seconds)  

---

## 1. Verified Video Deliverables

All video assets are saved in `C:\Users\sethi\HomeMind\submission\`:

| Deliverable File | Type | Specification | Verified Status |
| :--- | :--- | :--- | :---: |
| **`HomeMind_Final_Demo_Video_1080p.mp4`** | **Master Video** | **1920×1080 (16:9), 30 fps, H.264 (yuv420p), AAC 192k audio, 111.87s duration (~1 min 52s)** | ✅ **Verified** |
| `HomeMind_Demo_Video_1080p.mp4` | Video Stream | 1920×1080, 30 fps, MPEG-4 Part 2, burned-in captions, crossfade transitions | ✅ Verified |
| `narration_voiceover.wav` | Audio Master | SAPI5 synthesized voice narration normalized with padding pauses | ✅ Verified |
| `captions.srt` | Subtitle File | Standard SubRip (.srt) subtitle track for YouTube/Vimeo/Devpost | ✅ Verified |
| `DEMO_VIDEO_SCRIPT.md` | Script | Scene-by-scene script with timestamps and exact narration words | ✅ Verified |
| `STORYBOARD.md` | Storyboard | Shot-by-shot visual and transition plan | ✅ Verified |
| `scene1_problem.png` | Title Card | 1920×1080 problem definition graphic card | ✅ Verified |
| `scene2_dashboard.png` | Real App UI | 1920×1080 screenshot of live HomeMind React dashboard (port 5173 + 8081) | ✅ Verified |
| `scene3_watch.png` | Real App UI | 1920×1080 screenshot showing `set_temporary_watch` MCP tool execution & countdown | ✅ Verified |
| `scene4_alert.png` | Real App UI | 1920×1080 screenshot showing doorbell press matching active watch & alert banner | ✅ Verified |
| `scene4_focus.png` | Real App UI | 1920×1080 screenshot showing Focus Mode suppressing audible motion chimes | ✅ Verified |
| `scene5_recall.png` | Real App UI | 1920×1080 screenshot showing `what_happened` MCP tool conversational recall summary | ✅ Verified |
| `scene6_architecture.png` | Architecture Card| 1920×1080 cognitive pipeline diagram with 28/28 tests passing badge and closing quote | ✅ Verified |

---

## 2. Hackathon Video Requirements Verification

- [x] **Duration Under 120 Seconds**: Video is **111.87 seconds** (1 minute, 51.87 seconds), strictly complying with the 2-minute rule.
- [x] **16:9 Landscape 1080p Format**: Rendered in standard 1920×1080 resolution at 30.0 fps.
- [x] **Real Running Application Footage**: Scenes 2, 3, 4a, 4b, and 5 were captured directly from the live React single-page app interacting with the running FastAPI backend on ports 5173 and 8081 via Chrome DevTools Protocol.
- [x] **No Terminal Clutter / Distractions**: Captures focus purely on the clean dark-mode dashboard without browser tabs, bookmarks, or OS notifications.
- [x] **Clear Voice Narration & Burned-In Captions**: Spoken voiceover is synchronized with each scene; high-contrast lower-third captions ensure readability even with sound muted.
- [x] **Honest Implementation Boundaries**: Clearly states that Ring events are currently simulated, the Alexa+ client is modeled via a local MCP agent, and real physical hardware integrations are planned for the post-hackathon roadmap.

---

## 3. Devpost Submission Form Content

### Project Title
**HomeMind: Context-Aware Multi-Device AI Home Agent**

### Elevator Pitch (1-2 Sentences)
HomeMind is an intelligent context, memory, and decision layer that transforms smart home devices from noisy, isolated trigger scripts into a unified ambient presence. By reasoning over occupancy modes, active monitoring intentions, and attention thresholds, HomeMind determines what happened, whether it matters, and which device should communicate it.

### What It Does
- **Context-Aware Attention Management**: Eliminates notification fatigue by filtering raw sensor events through a 5-step cognitive pipeline.
- **Intent-Driven Temporary Watches**: Allows users to conversationally establish monitoring windows (e.g. *"Watch the front door for 30 minutes"*), adjusting attention thresholds on the fly.
- **Multimodal Routing**: Intelligently routes notifications to the appropriate interface—suppressing loud audio chimes in Focus mode in favor of subtle visual context cards.
- **Model Context Protocol (MCP)**: Exposes 6 standard tools (`get_home_status`, `what_happened`, `set_home_mode`, `set_temporary_watch`, `get_recent_events`, `clear_alert`) ready for Alexa+ Agent Skills.

### Amazon Ecosystem Role
- **Alexa+ / Echo**: Conversational interface and voice announcements using MCP tools.
- **Ring**: Event ingestion pipeline modeling doorbell chimes, perimeter motion, and contact sensors.
- **Fire TV**: Ambient visual display client for picture-in-picture banners and context cards.
- **AWS**: Cloud architecture designed for App Runner / ECS containerization, DynamoDB state persistence, and Amazon Bedrock reasoning.

### How to Run Locally (Verification)
1. Backend: `python -m uvicorn backend.main:app --port 8081`
2. Frontend: `cd frontend && npm run dev` (Port 5173)
3. Tests: `python -m pytest -v` (28/28 tests passed)
