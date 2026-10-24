# HomeMind Hackathon Demo Video Script 🎬

**Total Duration**: 120 Seconds (2:00 Max)  
**Target Video Format**: 16:9 Landscape (1920×1080), 30/60 FPS  
**Target Submission**: Amazon Build, Ship, Shape Hackathon (Devpost)  
**Narration Style**: Clear, confident, technical, ambient-focused  
**Word Count**: ~270 words (~135 words/minute = relaxed, professional pace)

---

## Complete Narration & Scene Breakdown

### Scene 1 — The Problem: Notification Fatigue
- **Time**: 0:00 – 0:15 (15s)
- **Visual**: Cinematic title card / Ambient Smart Home Dilemma graphic showing notification overload.
- **On-Screen Text**: "The Smart Home Problem: Every sensor interrupts. None understand context."
- **Narration**:
  > *"Today's smart homes are louder than ever. Every camera chime, backyard leaf flutter, or hallway sensor triggers an isolated push notification, interrupting dinner or deep work with the exact same urgency. Smart devices detect events—but they don't understand context."*

---

### Scene 2 — Meet HomeMind
- **Time**: 0:15 – 0:30 (15s)
- **Visual**: Live HomeMind Control Center at `http://localhost:5173`. Cursor pans over the Header, "Backend Online (Port 8081)" badge, Occupancy Mode badge (`home`), Active Watches counter, and Recent Events list.
- **On-Screen Text**: "HomeMind: Context, Memory, and Decision Layer for the Ambient Home"
- **Narration**:
  > *"Meet HomeMind. HomeMind is an intelligent context, memory, and decision layer. Built on Python, FastAPI, and standard Model Context Protocol servers, HomeMind maintains an evolving model of your home across Ring, Alexa, and Fire TV."*

---

### Scene 3 — User Intent: Temporary Watch via MCP
- **Time**: 0:30 – 0:50 (20s)
- **Visual**: HomeMind Conversation Panel. Type utterance into the prompt:
  `Watch the front door for 30 minutes.`
  Press Send. The chat displays HomeMind's response. The Active Watches panel updates instantly with a new card: `front_door`, 30 minutes, live countdown timer.
- **On-Screen Text**: "Alexa+ Agent Skill: set_temporary_watch tool execution"
- **Narration**:
  > *"Rather than configuring brittle automation routines, users simply express intent through Alexa. When I ask: 'Watch the front door for 30 minutes', HomeMind executes the `set_temporary_watch` MCP tool. A dynamic monitoring window is established with live countdown and prioritized attention thresholds."*

---

### Scene 4 — Event Ingestion & Context-Aware Decisions
- **Time**: 0:50 – 1:15 (25s)
- **Visual**: 
  1. Under Simulation Controls, click **Simulate Doorbell**.
  2. Active Alerts panel immediately highlights: "Doorbell pressed at front_door". The Decision Engine recognized the event matched our active watch and escalated an alert.
  3. Click **Set Focus Mode**. Mode flips to `focus`.
  4. Click **Simulate Motion**. The event is logged in Recent Events, but NO disruptive audible alert fires—preserving focus.
- **On-Screen Text**: "Decision Engine: 5-Step Cognitive Pipeline & Multimodal Routing"
- **Narration**:
  > *"Now let's simulate a physical Ring event. When a visitor rings the front doorbell, HomeMind correlates it with our active watch and immediately escalates an alert. But watch what happens in Focus mode. When perimeter motion occurs, HomeMind's Decision Engine suppresses intrusive audible chimes, logging the event quietly while keeping you in your flow."*

---

### Scene 5 — Conversational Recall & Short-Term Memory
- **Time**: 1:15 – 1:35 (20s)
- **Visual**: Return to Conversation Panel. Type:
  `What happened at the front door?`
  Press Send. HomeMind queries `MemoryManager` via `what_happened` tool and displays structured summary:
  *"Found 2 event(s) for front_door: doorbell_press at front_door, motion_detected at front_door."*
- **On-Screen Text**: "Conversational Memory: what_happened MCP tool"
- **Narration**:
  > *"When you're ready to catch up, there's no need to scrub through endless camera timelines. Simply ask Alexa+: 'What happened at the front door?' HomeMind queries its MemoryManager, synthesizing recent events into a concise, natural response."*

---

### Scene 6 — Architecture & Hackathon Wrap-Up
- **Time**: 1:35 – 2:00 (25s)
- **Visual**: Architecture Diagram highlighting the cognitive pipeline (Sensors $\rightarrow$ Context/Memory $\rightarrow$ Decision Engine $\rightarrow$ Multimodal Adapters $\rightarrow$ MCP Tools). Terminal split showing 28/28 tests passing. Closing title card with project tagline.
- **On-Screen Text**: "HomeMind: A smarter home doesn't just detect events. It understands when they matter."
- **Narration**:
  > *"HomeMind is powered by FastAPI, Pydantic, 6 Model Context Protocol tools, and a 28-test verified test suite. While today's demo runs locally with simulated Ring events and an Alexa-style MCP client, the architecture is ready for Amazon Agent Skills and AWS cloud deployment. HomeMind: A smarter home doesn't just detect events. It understands when they matter."*
