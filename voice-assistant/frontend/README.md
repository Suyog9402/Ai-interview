# AI Interview Platform - Next.js 15 Frontend

Modern Next.js 15 (App Router) frontend for the AI Interview Assistant platform, featuring real-time WebRTC audio visualization with LiveKit, MediaPipe computer vision face proctoring, and comprehensive recruiter & admin governance dashboards.

---

## 🌟 Features

- **Real-Time Voice Assistant Client**: WebRTC streaming via `@livekit/components-react` with live audio waveform visualization and low-latency interaction.
- **Client-Side Face Proctoring**: MediaPipe 468-point FaceMesh running directly in the browser via Canvas/WebAssembly, streaming real-time head orientation (yaw/pitch) and Eye Aspect Ratio (EAR) gaze tracking to backend WebSockets.
- **Recruiter & Admin Governance Panel**:
  - Candidate leaderboard and scorecards.
  - Granular breakdown of technical accuracy, completeness, clarity, speech delivery metrics, and proctoring telemetry.
  - Job description creation and version snapshots.
- **Role-Based Routing & Protected Portals**: Candidate assessment flow and administrative controls.

---

## 🚀 Setup & Execution

### 1. Install Dependencies
```bash
npm install
# or with pnpm:
pnpm install
```

### 2. Environment Configuration
Copy `.env.example` to `.env.local`:
```bash
cp .env.example .env.local
```

Configure your environment variables:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_LIVEKIT_URL=wss://your-project.livekit.cloud
```

### 3. Start Development Server
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### 4. Production Build & Typecheck
```bash
npm run build
npm run start
```
