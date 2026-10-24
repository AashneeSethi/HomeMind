# HomeMind Frontend Dashboard & Simulator

Modern React + Vite frontend providing a real-time ambient smart home dashboard and Alexa+ conversation simulator for HomeMind.

---

## Features

1. **Header & Live Connection**:
   - Connection health indicator (live polling to FastAPI backend at `http://localhost:8000`).
   - Real-time clock and status indicators.

2. **Occupancy & Ambient State**:
   - Live occupancy mode pills (`Home`, `Away`, `Sleep`, `Focus`).
   - Current ambient context summary calculated by HomeMind's `ContextManager`.
   - Metric cards: Active Watches, Active Alerts, Observed Devices, Ingested Events.

3. **Active Temporary Watches**:
   - Real-time countdown timer showing remaining seconds/minutes for focused location monitoring.
   - Cancel button for dismissing active watches.

4. **Active Alerts**:
   - Displays real-time security alerts (e.g., unexpected motion in away mode).
   - Dismiss and "Clear All" functionality.

5. **Alexa+ Conversational Interface**:
   - Interactive chat interface simulating Alexa+ voice interactions.
   - Routes natural language queries to backend MCP tools (`get_home_status`, `what_happened`, `set_home_mode`, `set_temporary_watch`, `get_recent_events`, `clear_alert`).
   - Displays which MCP tool was invoked and the structured agent reply.

6. **Event & Sensor Simulator (Ring Provider Sim)**:
   - One-click trigger buttons for Doorbell press, Front Door motion, Driveway vehicle, and Backyard motion.
   - Custom event trigger form with selectable locations and event types.

7. **Real-Time Event Stream**:
   - Scrollable feed of all ingested events with timestamps, device source, and location tags.

---

## How to Run

### Development Mode (with proxy to backend)

```bash
# In frontend/
npm run dev
```

App will run on `http://localhost:5173`.

### Production Build

```bash
# In frontend/
npm run build
npm run preview
```
