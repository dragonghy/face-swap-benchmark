========================================================
IMAGE‑GEN BENCHMARKING FRAMEWORK – PROJECT SPEC (v2)
========================================================
*Plain‑text / Markdown version – copy straight into a .txt or .md file.*

---

## 1  Overview  
Benchmark how well image‑generation tools can **swap** people in a
template photo with supplied avatar images.  
*New in v2*: an interactive local web UI that lets you create test cases,
choose tools, run the benchmark, and watch progress live.

---

## 2  Major Additions (v2)

| Feature | Description |
|---------|-------------|
| **Interactive Web UI** | Local site at **`http://localhost:8000`**. Lets the user pick test‑cases & tools, press **Run**, and see live progress + final results. |
| **Real‑Time Updates** | Progress bar, per‑task status, thumbnails appear as soon as they’re ready. Implemented with WebSockets or SSE. |
| **Results Dashboard** | Grid view (test‑cases × tools) with machine score badge and editable 1–5‑star human rating. “Export Report” downloads a static HTML snapshot. |

---

## 3  Functional Requirements (Delta Only)

### Web Server  
* **FastAPI** + **Starlette** for WebSockets  
* Static assets (JS/CSS) served from `web/static/`

### API Endpoints  

GET  /                → SPA shell
GET  /api/test‑cases  → list test cases
GET  /api/tools       → list registered tools
POST /api/run         → start run {case_ids[], tool_ids[], options} → run_id
WS   /api/run/{id}    → progress events
POST /api/rate        → save human score {run_item_id, stars}

### Progress Events (JSON)  
```json
{ "type": "update",
  "case_id": "tc_01",
  "tool_id": "baseline_gpt",
  "status": "generated",
  "image_url": "/runs/2025‑04‑20/baseline_gpt/tc_01.png",
  "score": null }

Persistence
	•	SQLite tables: runs, run_items, human_scores
	•	Images & JSON cached under runs/<date>/<tool>/<case>.png

⸻

4  Revised Directory Layout

benchmark/
  cli.py
  config.py
  core/
    models.py
    runner.py
    evaluator.py
    plugins/
      baseline_gpt.py
      baseline_dalle3.py
  web/                  ← NEW
    main.py             # FastAPI app
    sockets.py          # WebSocket manager
    templates/
      index.html
    static/             # built via Vite or plain ES‑modules
      app.js
      app.css
  report/
    report_builder.py
  utils/
    image_io.py
datasets/
runs/
README.md



⸻

5  Minimum Viable UI Flow
	1.	Open localhost:8000 → gallery of test cases.
	2.	Tick Baseline‑GPT and Baseline‑DALL·E 3 (or others).
	3.	Click Run Benchmark.
	4.	Watch live status rows: queued → generating → evaluating → scored.
	5.	When finished, grid view appears; adjust human ratings.
	6.	Click Export Report to download report_<run_id>.html.

⸻

6  Technology Notes
	•	Use asyncio tasks + semaphore for concurrency.
	•	Choose SSE if you only need server→client updates; upgrade to
WebSockets for bidirectional control.
	•	Hot‑reload dev server:

uvicorn web.main:app --reload



⸻

7  Deliverables
	•	Python package benchmark (3.10+).
	•	Built‑in baselines: baseline_gpt.py, baseline_dalle3.py.
	•	generate‑cases, run, and report CLI commands.
	•	Fully‑functional web interface with live progress & rating UI.
	•	≥ 3 auto‑generated test cases for demo.
	•	README with setup & usage instructions.

⸻



