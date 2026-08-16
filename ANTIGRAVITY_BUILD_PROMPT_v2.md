# AI-Agent System for Startup Automation — Full Build Prompt v2 (Antigravity)

> **What changed from v1:** v1 used Next.js + Supabase + TypeScript end-to-end. Your approved
> proposal (Section 6, "Components/Software List") explicitly commits to **Python 3.x, LangChain
> and/or CrewAI, FastAPI, Streamlit, SQLite/PostgreSQL, Pandas/NumPy, Matplotlib/Plotly**. This
> version rebuilds the plan around that stack — **without discarding the Next.js "Cofounder"
> landing page you've already built.**

> **Architecture in one line:** Your existing Next.js landing page stays exactly as-is. A new
> **Python/FastAPI backend** (with **LangChain/CrewAI**-orchestrated agents, **SQLite→PostgreSQL**
> storage, **Pandas/NumPy** analytics, **Matplotlib/Plotly** charts) becomes the real product. The
> authenticated app screens are new Next.js pages that call this backend over REST — same repo,
> same Cofounder visual language, zero changes to what you already shipped. A small internal
> **Streamlit** dashboard also exists purely to satisfy the "Streamlit" line item in your proposal
> and to let you (and your guide) sanity-check each agent in isolation without opening the UI.

---

## How to use this file

Paste **one `PROMPT` block at a time** into Antigravity, in order. Confirm each step works before
moving to the next. Paste **Prompt 0** as pinned/persistent context (`agents.md` or equivalent)
first — every later prompt depends on it silently.

**Do not let Antigravity touch, rename, restructure, or "improve" anything already inside your
Next.js app's marketing/landing route or its existing components.** Every prompt below says this
explicitly, but it's worth stating once up front: the landing page is frozen. Everything new is
additive.

---

## PROMPT 0 — Project Rules (paste as `agents.md` / pinned system context)

```
You are extending an existing repo. It already contains a Next.js 14 (App Router, TypeScript,
Tailwind) project with ONE finished piece: a "Cofounder"-styled public landing page (marketing
route group, hero sections, nav, illustrations, etc.). DO NOT edit, refactor, rename, or delete
any file currently used by that landing page or its existing components/styles. Treat it as
frozen, reference-only. If a new feature seems to require changing a landing-page file, stop and
ask instead of changing it.

GOAL: Build the actual product behind that landing page — "AI-Agent System for Startup
Automation" — a Coordinator Agent that routes founder requests to five specialist agents
(Customer Support, Sales Outreach, Content Creation, Marketing & Ads, Data Analytics).

STACK (matches the approved academic proposal — do not deviate without asking):
- Backend: Python 3.11+, FastAPI, Uvicorn
- Agent orchestration: LangChain and CrewAI — the Coordinator is a CrewAI Crew (or LangChain
  Router if that fits better for a given step; default to CrewAI for the multi-agent crew itself)
- LLM: Anthropic Claude API (model claude-sonnet-4-6) via LangChain's ChatAnthropic integration —
  this satisfies the proposal's "OpenAI API / compatible LLM services" line as a compatible
  managed LLM service; do not add a second LLM provider unless asked
- Database: SQLAlchemy ORM. SQLite (`app.db`) for local dev, swappable to PostgreSQL via a single
  DATABASE_URL env var for deployment — satisfies "SQLite/PostgreSQL"
- Data processing: Pandas + NumPy for every analytics computation — never hand-roll aggregation
  logic in Python loops, use Pandas DataFrames
- Charts: Matplotlib for any server-rendered static chart image, Plotly for any interactive chart
  JSON handed to the frontend — satisfies "Matplotlib/Plotly"
- Internal testing UI: a single Streamlit app (`streamlit_admin/app.py`) that lets you run any
  agent directly against the FastAPI backend and see raw input/output — this is a developer/demo
  tool, never the main product UI, and must never be advertised as the founder-facing product
- Frontend (founder-facing, authenticated app): the EXISTING Next.js project. Add new routes
  under a new route group (e.g. `/app/(product)/...`) that call the FastAPI backend over REST
  (fetch to NEXT_PUBLIC_API_URL). Reuse the landing page's visual language (colors, type,
  illustration style) for new pages, but build new components as needed — don't be blocked by
  "must reuse the exact same component file" if the landing page's components weren't built to be
  reused; duplicating a small presentational component is fine, breaking the landing page is not.
- Auth: FastAPI backend issues JWTs (simple email/password, passlib for hashing, python-jose for
  JWT). Next.js stores the token (httpOnly cookie via a Next.js route handler that proxies to
  FastAPI) and attaches it to every backend call. No third-party auth provider needed.
- Deploy target: FastAPI backend on Render or Railway; Next.js frontend stays on Vercel
  (unchanged from however it's deployed today).

ARCHITECTURE:
- A central Coordinator Agent (CrewAI Crew, or a LangChain classifier feeding into CrewAI tasks)
  reads a natural-language founder request and routes it to one or more of five specialist
  agents: customer_support, sales_outreach, content_creation, marketing_ads, analytics.
- Every agent is a Python function/class with a consistent contract:
    def run(company_id: str, instruction: str, context: dict | None = None) -> AgentResult
  where AgentResult = { "summary": str, "data": dict | None, "log_entry": str }
- Every agent call writes a row to `activity_log` — never fake or hardcode activity entries in
  the frontend; it always reflects real backend writes.
- Every table is scoped by `company_id`. Every FastAPI route checks the JWT's user owns that
  company before touching any row for it.
- No plaintext secrets in code — everything through env vars / `.env` (gitignored).

VISUAL IDENTITY (for new authenticated-app pages only — do not restyle the landing page):
- Match the landing page's palette and type as closely as the existing code lets you infer it
  (warm off-white background, cream cards, navy ink text, blue primary accent). If you can't
  cleanly extract exact tokens from the landing page code, ask before inventing new ones.
- Reuse the "chapter hero / callout card / step diagram / pixel illustration" visual grammar for
  new app pages so the product feels continuous with the landing page, without editing the
  landing page's own files.

NEVER:
- Never modify a file under the landing page's route group or its dedicated components without
  explicit confirmation.
- Never fabricate agent output or analytics numbers in the UI — everything traces back to a real
  FastAPI response backed by a real DB row.
- Never commit `.env`, `.env.local`, `app.db`, or any secret.
- Never skip LangChain/CrewAI and call the Claude API "raw" from an agent — route every agent's
  LLM call through the LangChain/CrewAI layer so the proposal's declared orchestration stack is
  actually exercised, not just imported and unused.

Confirm you've understood this, and confirm you can see the existing Next.js landing page files
without modifying any of them, before starting Prompt 1.
```

---

## PROMPT 1 — Backend scaffold (Python/FastAPI, additive to the repo)

```
Inside the existing repo, create a new top-level `backend/` folder — completely separate from
the Next.js app — with this structure:

  backend/
    app/
      main.py                 -> FastAPI app, CORS config allowing the Next.js origin
      core/
        config.py              -> pydantic Settings reading env vars (DATABASE_URL,
                                   ANTHROPIC_API_KEY, JWT_SECRET, FRONTEND_ORIGIN)
        security.py            -> password hashing (passlib), JWT create/verify (python-jose)
        db.py                  -> SQLAlchemy engine/session, works with sqlite:/// locally and
                                   postgresql:// in prod off the same DATABASE_URL
      models/                  -> SQLAlchemy ORM models (empty for now, filled in Prompt 2)
      schemas/                 -> Pydantic request/response schemas (empty for now)
      agents/                  -> LangChain/CrewAI agent implementations (empty for now)
      routers/                 -> FastAPI routers (empty for now)
      services/                -> shared business logic helpers
    tests/
    requirements.txt           -> fastapi, uvicorn[standard], sqlalchemy, pydantic-settings,
                                   langchain, langchain-anthropic, crewai, pandas, numpy,
                                   matplotlib, plotly, passlib[bcrypt], python-jose[cryptography],
                                   python-multipart, streamlit
    .env.example                -> DATABASE_URL, ANTHROPIC_API_KEY, JWT_SECRET, FRONTEND_ORIGIN
    Dockerfile                  -> for deploying to Render/Railway later

Also create `backend/streamlit_admin/app.py` as an empty placeholder for now (filled in later
prompt) and add `backend/` entries to the repo root `.gitignore` (`.env`, `app.db`,
`__pycache__/`, `.venv/`).

Do NOT touch anything under the existing Next.js app's landing page route. Confirm
`uvicorn app.main:app --reload` boots and `GET /health` (add a trivial health route) returns
`{"status": "ok"}` before moving on.
```

---
Continue the pending task from the current state. Do not restart or redo completed work. First inspect the existing changes, git diff, task history, and current project state. Determine exactly what remains unfinished, then continue from the last completed step. Preserve all working changes and run the relevant tests/checks before considering the task complete.
---

## PROMPT 2 — Database schema (SQLAlchemy)

```
In `backend/app/models/`, define SQLAlchemy models for:

- User: id (uuid pk), email (unique), hashed_password, created_at
- Company: id (uuid pk), owner_id (fk -> User.id), name, industry, icp (text), brand_voice,
  created_at
- ActivityLog: id (uuid pk), company_id (fk), agent (str), instruction (text), summary (text),
  created_at
- SupportTicket: id (uuid pk), company_id (fk), customer_message (text), ai_reply (text nullable),
  tag (str nullable: billing|bug|onboarding|other), escalated (bool default False),
  status (str default "open"), created_at
- Lead: id (uuid pk), company_id (fk), name, company_name, email, tier (str: "Tier 1"/"Tier 2"/
  "Tier 3"), stage (str default "Open", one of Open/Trying to Contact/Contacted/Consult/Pitch/
  Verbal Commit/Closed Won/Closed Lost), created_at
- Sequence: id (uuid pk), lead_id (fk), day (int), channel (str: email|social|dm), content (text),
  sent (bool default False)
- ContentItem: id (uuid pk), company_id (fk), type (str: blog|social|caption|landing),
  topic (text), body (text), status (str default "draft": draft|approved|published), created_at
- Campaign: id (uuid pk), company_id (fk), goal (text), budget (numeric), channel_mix (JSON),
  ad_variants (JSON), created_at

Use `sqlalchemy.orm.declarative_base`, UUID primary keys stored as strings for SQLite
compatibility (works unmodified under PostgreSQL too). Add an Alembic setup
(`backend/alembic/`) so schema changes are version-controlled migrations, not just
`Base.metadata.create_all` — initialize it, generate the first migration
(`0001_init`) covering all tables above, and confirm `alembic upgrade head` creates a working
`app.db`.

Add a `backend/app/services/authz.py` helper `assert_owns_company(user_id, company_id, db)` that
every router will call before touching company-scoped data — raise HTTP 403 if the user doesn't
own that company. This is the single place ownership is checked; routers must call it, never
re-implement the check inline.
```

---

## PROMPT 3 — Auth (FastAPI + JWT, Next.js integration)

```
Implement:
- `backend/app/routers/auth.py`: POST /auth/signup (email+password -> creates User, hashes pw),
  POST /auth/login (returns a JWT), GET /auth/me (returns current user from JWT).
- `backend/app/routers/companies.py`: POST /companies (create a company for the current user —
  this is "onboarding"), GET /companies/me (the current user's company).
- A FastAPI dependency `get_current_user` that reads the Bearer token, verifies it, loads the
  User from DB, raises 401 if invalid/missing.

On the Next.js side, ADD (do not touch existing files) a new route group, e.g.
`/app/(product)/`, with:
- `/app/(product)/login/page.tsx` and `/signup/page.tsx` — simple forms that POST to the FastAPI
  backend via a thin Next.js route handler (`/app/api/auth/[...].ts`) that proxies the request and
  sets an httpOnly cookie with the JWT — never store the JWT in localStorage.
- Middleware protecting everything under `/app/(product)/app/*`, redirecting to `/login` if no
  valid cookie.
- On first login with no company yet, redirect to an onboarding page (name, industry, icp,
  brand_voice form) that POSTs to `/companies`.

Style these new pages using the landing page's palette/type by inspecting its existing Tailwind
config and components — but build them as new files. Confirm signup -> onboarding -> a blank
authenticated shell page works end to end before continuing.
```

---

## PROMPT 4 — Agent 1 + Coordinator skeleton (Customer Support)

*(Phase-per-agent starts here — build and verify one agent at a time rather than all five at
once, so each is independently demoable.)*

```
In `backend/app/agents/`, set up the shared LangChain/CrewAI scaffolding first:
- `llm.py`: a single shared `ChatAnthropic(model="claude-sonnet-4-6")` instance (via
  `langchain-anthropic`), read `ANTHROPIC_API_KEY` from settings.
- `base.py`: an `AgentResult` Pydantic model (summary: str, data: dict | None, log_entry: str),
  and an `AGENTS: dict[str, Callable]` registry that later agents register themselves into.
- `coordinator.py`: a CrewAI Crew with one "Coordinator" agent whose job is classification only.
  Give it a task that must return strict JSON:
    { "agent": "customer_support"|"sales_outreach"|"content_creation"|"marketing_ads"|
               "analytics"|"multi",
      "reasoning": "short reason",
      "subtasks": [ { "agent": "...", "instruction": "..." } ] }
  Strip markdown code fences before `json.loads`; wrap in try/except with a safe fallback
  ({"agent": "customer_support", "reasoning": "fallback", "subtasks": [...]}) if parsing fails.
  For now (until other agents exist), `coordinator.py` can only actually dispatch to
  customer_support — leave TODO comments for the rest, added in later prompts.

Now implement the first real agent, `backend/app/agents/customer_support.py`:
- Input: a customer message (+ optional existing ticket id).
- Build a LangChain chain (prompt template -> ChatAnthropic -> output parser) that: does a
  lightweight retrieval pass over that company's recent SupportTicket rows (simple keyword
  match via Pandas — no vector DB needed), then asks Claude to draft a reply, classify a tag
  (billing|bug|onboarding|other), and set an escalation flag if not confident. Require strict
  JSON output.
- Insert/update a SupportTicket row via SQLAlchemy. Return an AgentResult with a one-sentence
  summary and log_entry.
- Register it in the AGENTS registry.

Add `backend/app/routers/agents.py` with:
  POST /agents/coordinator   { company_id, message } -> coordinator result (writes activity_log)
  POST /agents/support       { company_id, message, ticket_id? } -> runs customer_support directly
Both check `assert_owns_company` first.

Write `backend/tests/test_support_agent.py` that calls the agent function directly with sample
input and asserts a SupportTicket row was created. Run it and paste me the output before we move
to the next agent.
```

---

## PROMPT 5 — Agent 2 (Sales Outreach) + Coordinator update

```
Implement `backend/app/agents/sales_outreach.py`:
- Input: an ICP description + one or more lead names/companies.
- LangChain chain asks Claude for: a personalized cold email, a 4–5 day follow-up cadence
  (Day 1 email, Day 2 social touch, Day 3 email, Day 4 social touch, Day 5 email), and a
  Tier 1/2/3 score with one-line reasoning. Strict JSON output.
- Insert/update a Lead row, insert Sequence rows per day.
- Register it in AGENTS.

Update `coordinator.py` so its dispatch logic can now route to `sales_outreach` in addition to
`customer_support` — update the classification prompt's examples accordingly.

Add `POST /agents/sales { company_id, icp, leads: [...] }` to the agents router.

Extend `test_support_agent.py`'s pattern into `test_sales_agent.py`. Run both tests, paste output,
then confirm the Coordinator correctly routes at least 2 sample prompts — one that should hit
customer_support, one that should hit sales_outreach — via `POST /agents/coordinator`.
```

---

## PROMPT 6 — Agent 3 (Content Creation) + Coordinator update

```
Implement `backend/app/agents/content_creation.py`:
- Input: content type (blog|social|caption|landing), topic, and the company's brand_voice
  (pulled from the Company row).
- LangChain chain drafts the content in that brand voice. Insert a ContentItem row with
  status "draft".
- Register it in AGENTS. Update the Coordinator's classification prompt to include this agent.
- Add `POST /agents/content { company_id, type, topic }`.

Write `test_content_agent.py`. Run it, paste output, and re-run the Coordinator routing check
from Prompt 5 with a third sample prompt that should hit content_creation.
```

---

## PROMPT 7 — Agent 4 (Marketing & Ads) + Coordinator update

```
Implement `backend/app/agents/marketing_ads.py`:
- Input: budget, target audience description, goal (awareness|signups|sales).
- LangChain chain returns: a suggested channel mix (JSON: channel -> % of budget), 2–3 ad copy
  variants, short targeting suggestions. Insert a Campaign row (channel_mix and ad_variants as
  JSON columns).
- Register it in AGENTS. Update the Coordinator's classification prompt.
- Add `POST /agents/marketing { company_id, budget, audience, goal }`.

Write `test_marketing_agent.py`. Run it, paste output, and extend the Coordinator routing check
with a fourth sample prompt for marketing_ads.
```

---

## PROMPT 8 — Agent 5 (Data Analytics — Pandas/NumPy/Matplotlib/Plotly)

```
Implement `backend/app/agents/analytics.py`. This agent does NOT call Claude for its numbers —
only for the natural-language summary at the end. Steps:

1. Pull raw rows for a company_id: leads (by stage), tickets (by status/tag), content items
   (by status), campaigns (with budgets), activity_log (volume by agent, last 7/30 days).
2. Load each into a Pandas DataFrame and compute aggregates with Pandas/NumPy — group-by counts,
   percentage breakdowns, rolling activity volume. Do not hand-roll aggregation with raw Python
   loops; use DataFrame operations.
3. Build:
   - A Matplotlib figure (e.g. activity_log volume over time, or lead-stage funnel) saved to a
     PNG, base64-encoded, returned in the response for the frontend to render as an <img>.
   - A Plotly figure (JSON, via `fig.to_json()`) for an interactive chart the frontend renders
     with `react-plotly.js` (or embeds via an iframe if simpler) — pick the same or a
     complementary chart to the Matplotlib one so both libraries are genuinely exercised.
4. Feed ONLY the already-computed Pandas numbers (never raw rows) to Claude via LangChain, asking
   for a short natural-language summary ("This week: 12 leads contacted, 3 replies, 40% ticket
   auto-resolution..."). Claude must not invent numbers — pass the computed dict directly into
   the prompt template as context.
5. Register in AGENTS, update Coordinator's classification prompt (this is likely to be
   classified as "analytics" for read-style requests, or "multi" if bundled with others).
6. Add `GET /agents/analytics?company_id=...`.

Write `test_analytics_agent.py` seeding a few rows via the ORM first, then asserting the returned
numbers match a manual Pandas computation on the same seed data. Run it and paste output.

At this point all 5 agents + Coordinator are done. Run a final Coordinator routing test with 5
distinct sample prompts (one per agent) plus one that should produce "multi" and dispatch to two
agents at once — write this as `backend/tests/test_coordinator_routing.py` and paste me the
output.
```

---

## PROMPT 9 — Streamlit admin/testing dashboard

```
Build `backend/streamlit_admin/app.py`: a single-file Streamlit app, run with
`streamlit run streamlit_admin/app.py`, that:
- Lets you pick a company_id (dropdown populated from the DB) and an agent (radio buttons:
  Coordinator, Customer Support, Sales Outreach, Content Creation, Marketing & Ads, Analytics).
- Shows a form with the right input fields for whichever agent is selected.
- On submit, calls the agent function directly (import from `backend.app.agents`, not over HTTP —
  this is a dev tool, it can talk to the DB/agents in-process) and displays the raw AgentResult
  JSON plus a human-readable summary.
- For the Analytics agent, render the returned Matplotlib PNG and the Plotly figure directly in
  Streamlit (`st.image`, `st.plotly_chart`).

Label this clearly in a header: "Internal agent testing tool — not the founder-facing product."
This satisfies the proposal's Streamlit requirement as a genuine testing/demo interface, separate
from the Next.js product. Confirm it runs and you can exercise all 5 agents + Coordinator through
it without touching the FastAPI/Next.js layers.
```

---

## PROMPT 10 — FastAPI routes hardening + CORS + frontend wiring

```
Review every router built in Prompts 3–8 and confirm each one:
1. Requires a valid JWT (via `get_current_user`).
2. Calls `assert_owns_company` before any DB read/write scoped to a company_id.
3. Validates the request body with Pydantic schemas (add any missing ones under
   `backend/app/schemas/`).
4. Returns consistent error shapes (4xx with a `detail` message) instead of raw tracebacks.

Configure CORS in `main.py` to allow only `FRONTEND_ORIGIN` (from env) with credentials.

On the Next.js side, inside the new `/app/(product)/` route group only, build:
- `/app/(product)/app/dashboard/page.tsx` — welcome header with company name, a grid of 5 agent
  cards linking to their pages, a chat bar that POSTs to the FastAPI Coordinator endpoint and
  shows a pulsing "thinking" state, then the synthesis + which agents ran, plus a recent-activity
  sidebar.
- One page per agent under `/app/(product)/app/agents/{support,sales,content,marketing,
  analytics}/page.tsx`, each calling its matching FastAPI route and rendering real returned data
  (tickets list, leads table + cadence, content kanban, campaign channel-mix chart + ad copy
  cards, and for analytics: the Matplotlib PNG + an interactive Plotly chart via
  `react-plotly.js`).
- `/app/(product)/app/activity/page.tsx` — paginated activity_log timeline, filterable by agent.
- `/app/(product)/app/settings/page.tsx` — edit company name/industry/icp/brand_voice.

Style all of these consistently with the landing page's existing palette/type — reuse visual
patterns (hero banners, callout cards, step diagrams, empty states with an illustration) but as
new components under `/components/product/` so nothing in the landing page's own component
folder is touched. Every page needs a designed empty state (never a bare blank page).

Test the full chain: sign up -> onboard -> dashboard -> ask the Coordinator something that should
hit two agents -> see both results synthesized and reflected in the Activity timeline. Paste me
that walkthrough before moving on.
```

---

## PROMPT 11 — Seed data + polish for demo

```
Write `backend/scripts/seed.py` that, given a company_id, inserts realistic sample data via the
ORM: 6–8 leads across different stages/tiers with sequences, 5–6 support tickets in different
states, 4–5 content items across draft/approved/published, 2 campaigns, and a matching spread of
activity_log rows with timestamps over the last 14 days so the Analytics agent's Pandas
aggregates and charts have something meaningful to show. Run it once and confirm every page
(Dashboard, each Agent page, Activity) looks intentional and populated.

Then do a final pass:
- Confirm the Matplotlib PNG and Plotly chart both render correctly on the Analytics page.
- Confirm the Coordinator's chat bar thinking-state animation and every new page's entrance
  animation are smooth.
- Confirm mobile responsiveness on Dashboard and at least one agent page.
- Confirm the landing page is completely unaffected — click through it and diff `git status`
  against the landing-page files to prove nothing there changed.
```

---

## PROMPT 12 — Testing & security checklist

```
Run through and confirm each of the following, fixing anything that fails:

- [ ] Coordinator correctly routes at least 6 distinct sample prompts (one per agent + one
      multi-agent case) — from `test_coordinator_routing.py`, output pasted.
- [ ] Each specialist agent works when called directly via its own page AND via the Streamlit
      admin tool, not only via the Coordinator.
- [ ] Ownership check confirmed: create a second test user/company and verify FastAPI returns 403
      when it tries to access the first company's tickets/leads/content/campaigns/activity via a
      direct API call (curl/Postman), not just that the UI hides it.
- [ ] Every new app page has a designed empty state.
- [ ] Activity log updates within a couple seconds of any agent action.
- [ ] Analytics numbers (from the Pandas aggregation) match a manual spot-check query against the
      DB directly.
- [ ] No secrets committed; `backend/.env` and `app.db` are gitignored; confirm with `git status`.
- [ ] Landing page files show zero diffs from before this build started.
```

---

## PROMPT 13 — Deploy

```
1. git init (if not already), commit everything, push to GitHub.
2. Deploy `backend/` to Render or Railway (Dockerfile from Prompt 1): set DATABASE_URL to a
   managed PostgreSQL instance, ANTHROPIC_API_KEY, JWT_SECRET, FRONTEND_ORIGIN. Run
   `alembic upgrade head` against the production DB.
3. Deploy the Next.js app to Vercel as usual (landing page unaffected), setting
   NEXT_PUBLIC_API_URL to the deployed backend URL.
4. Re-run the Prompt 12 checklist against production, not just localhost.
5. Give me the final production URLs (frontend + backend) and a short note on anything that
   behaved differently in production vs. local dev.
```

---

## Appendix A — Mapping to your approved proposal

| Proposal item (Section 6 / methodology) | Where it's satisfied here |
|---|---|
| Python 3.x | Entire `backend/` (FastAPI, agents, tests, seed script) |
| OpenAI API / compatible LLM services | `ChatAnthropic` via LangChain — a compatible managed LLM service |
| LangChain and/or CrewAI | Every agent's LLM call goes through LangChain chains; Coordinator is a CrewAI Crew |
| FastAPI + REST APIs | `backend/app/routers/*`, all REST endpoints |
| Streamlit | `backend/streamlit_admin/app.py` — internal agent-testing prototype |
| SQLite / PostgreSQL | SQLAlchemy + Alembic, SQLite locally, PostgreSQL in prod via `DATABASE_URL` |
| Pandas / NumPy | All analytics aggregation in `agents/analytics.py` |
| Matplotlib / Plotly | Both used in the Analytics agent's chart generation |
| Git / GitHub | Prompt 13 |
| VS Code / Postman | Manual testing steps throughout (curl/Postman checks in Prompts 3, 10, 12) |
| 5 specialist agents + Coordinator | Prompts 4–8 |
| API & Data Layer | `backend/app/routers/`, SQLAlchemy models, Company/ActivityLog tables |

## Appendix B — Suggested phase-by-phase milestones (per-agent, as you asked)

- **Milestone 1 (infra):** Prompts 0–3 — backend scaffold, schema, auth wired to your existing
  Next.js landing page's repo without touching it.
- **Milestone 2 (Coordinator + Support):** Prompt 4 — first demoable agent + routing skeleton.
- **Milestone 3 (Sales):** Prompt 5.
- **Milestone 4 (Content):** Prompt 6.
- **Milestone 5 (Marketing):** Prompt 7.
- **Milestone 6 (Analytics):** Prompt 8 — all 5 agents + Coordinator complete and routing-tested.
- **Milestone 7 (Streamlit + frontend wiring):** Prompts 9–10 — internal test tool + real
  founder-facing pages built on top of the existing landing page.
- **Milestone 8 (demo-ready):** Prompts 11–13 — seed data, checklist, deploy.

Each milestone is independently screenshot-able for your progress reports/PPTs — you don't need
to wait until the whole thing is done to show working progress to your guide.

---

*End of build prompt v2. Paste Prompt 0 first as pinned context, then Prompts 1 through 13 one at
a time into Antigravity, confirming each milestone works before moving to the next.*
