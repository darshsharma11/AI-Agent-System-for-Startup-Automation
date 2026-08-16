# Cofounder-Style AI Agent Platform — Full Build Prompt for Antigravity

> **What this file is:** A complete, copy-paste-ready set of prompts for **Antigravity** (or any
> agentic coding tool) that builds your Sem V Mini Project end to end — frontend, backend,
> database, and the multi-agent system — styled visually like **cofounder.co**.
>
> **Project:** *AI-Agent System for Startup Automation* — a Coordinator Agent that routes
> founder requests to five specialist agents (Customer Support, Sales Outreach, Content
> Creation, Marketing & Ads, Data Analytics), all inside one dashboard.
>
> **Visual reference:** cofounder.co's "How To Start A Company" guide + product screenshots —
> pixel-art illustrations, chapter-style hero banners, colored callout cards ("Founder Move" /
> "Watch Out" / checklists), step diagrams, and a calm cream/blue/green palette.

---

## How to use this file

Don't paste the whole document into Antigravity at once. Paste **one `PROMPT` block at a
time**, in order, and let the agent finish + you sanity-check before moving to the next one.
Each prompt is self-contained but assumes everything from the earlier prompts already exists.

If Antigravity supports a persistent "project rules" or `agents.md`-style file, paste **Prompt 0**
in as that file first — it never changes, and every later prompt can silently rely on it.

---

## PROMPT 0 — Project Rules (paste as `agents.md` / system context, keep pinned)

```
You are building "Cofounder AI" (working name — feel free to suggest better ones, but keep this
until told otherwise): a multi-agent AI platform that automates startup operations for founders.

STACK (do not deviate without asking):
- Next.js 14+, App Router, TypeScript, Tailwind CSS
- Supabase (Postgres + Auth + Row Level Security) for all persistence and auth
- Anthropic Claude API (model: claude-sonnet-4-6, endpoint /v1/messages) for every agent's reasoning
- Framer Motion for animation
- Recharts for charts
- Deploy target: Vercel

ARCHITECTURE:
- A central Coordinator Agent classifies a natural-language founder request and routes it to one
  or more of five specialist agents: customer_support, sales_outreach, content_creation,
  marketing_ads, analytics.
- Every agent is a TypeScript async function with the identical signature:
  type AgentInput = { companyId: string; instruction: string; context?: Record<string, unknown> };
  type AgentResult = { summary: string; data?: Record<string, unknown>; logEntry: string };
  type Agent = (input: AgentInput) => Promise<AgentResult>;
- Every agent call writes a row to `activity_log` so the UI has a live, truthful timeline —
  never fake or hardcode activity entries.
- Every table is scoped by `company_id` and protected with Postgres Row Level Security tied to
  `auth.uid()`. No custom auth. No plaintext secrets in code — everything through env vars.

VISUAL IDENTITY — clone the "Cofounder" aesthetic from the attached reference guide/screenshots:
- Warm off-white background (#FDFCF7), cream cards (#F4F2EA), navy ink text (#14213D).
- Callout cards: blue "Agent Tip" boxes, amber "Watch Out" boxes, cream checklists with circular
  bullets that visually fill in when a real task/step completes.
- Big two-line bold hero headlines on every major page, small uppercase monospace eyebrow labels
  (e.g. "AGENT · SALES OUTREACH"), a 1-sentence subtitle, 3 bullet highlights.
- Flat pixel-art illustrations (rocket launch, robot arms, satellite dish, train) as SVGs in
  /public/illustrations — decorative companions to real hero sections and empty states, never
  load-bearing for information.
- Numbered step diagrams (circle → line → circle) for pipelines: Coordinator routing, sales
  cadence, deployment flow.
- Horizontal funnel bars with % labels for analytics/conversion visuals.
- Motion: sections fade + slide up on entrance (300–400ms, 60ms stagger), agent "thinking" state
  is a pulsing "●●●" not a generic spinner, checklist items scale+fill when checked.

NEVER:
- Never hand-roll authentication or password storage — Supabase Auth only.
- Never leave a page with a broken/empty look — every page needs a designed empty state with a
  pixel illustration + one clear call to action.
- Never fabricate data in the UI — analytics numbers must come from real Supabase rows.
- Never commit .env* files.

Confirm you've understood this before starting Prompt 1. Ask before deviating from the stack or
schema below.
```

---

## PROMPT 1 — Scaffold the project

```
Scaffold a new Next.js 14 project called `cofounder-ai` using TypeScript, Tailwind CSS, and the
App Router. Then install:
  @supabase/supabase-js @supabase/ssr framer-motion recharts lucide-react zod

Set up the folder structure:
  /app
    /(marketing)        -> public landing page
    /(auth)              -> login, signup
    /(app)                -> everything behind auth (dashboard, agents, activity, settings)
    /api                 -> route handlers
  /components/ui         -> shared design-system components
  /lib/agents             -> agent functions + coordinator
  /lib/supabase            -> client + server Supabase helpers
  /public/illustrations   -> pixel-art SVGs
  /scripts                -> seed.ts

Add a root `.gitignore` that excludes `.env*`, `node_modules`, `.next`. Add a placeholder
`.env.local.example` listing (without values):
  NEXT_PUBLIC_SUPABASE_URL
  NEXT_PUBLIC_SUPABASE_ANON_KEY
  SUPABASE_SERVICE_ROLE_KEY
  ANTHROPIC_API_KEY

Do not write any business logic yet. Just confirm the app boots with `npm run dev` and shows the
default Next.js page.
```

---

## PROMPT 2 — Database schema (Supabase)

```
Using the Supabase MCP/CLI (or by generating a SQL migration file if no direct connection is
available), create the following schema and enable Row Level Security on every table, scoped so
a user can only ever read/write rows belonging to a company they own.

-- companies (one workspace per founder/team)
create table companies (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid references auth.users(id) not null,
  name text not null,
  industry text,
  icp text,                 -- ideal customer profile description
  brand_voice text,
  created_at timestamptz default now()
);

-- activity log = the visible Coordinator timeline
create table activity_log (
  id uuid primary key default gen_random_uuid(),
  company_id uuid references companies(id) not null,
  agent text not null,       -- 'coordinator' | 'sales_outreach' | 'customer_support' | ...
  instruction text not null,
  summary text not null,
  created_at timestamptz default now()
);

-- customer support
create table support_tickets (
  id uuid primary key default gen_random_uuid(),
  company_id uuid references companies(id) not null,
  customer_message text not null,
  ai_reply text,
  tag text,                  -- billing | bug | onboarding | other
  escalated boolean default false,
  status text default 'open',
  created_at timestamptz default now()
);

-- sales outreach
create table leads (
  id uuid primary key default gen_random_uuid(),
  company_id uuid references companies(id) not null,
  name text, company_name text, email text,
  tier text,                 -- Tier 1 | Tier 2 | Tier 3
  stage text default 'Open', -- Open, Trying to Contact, Contacted, Consult, Pitch, Verbal Commit, Closed Won, Closed Lost
  created_at timestamptz default now()
);

create table sequences (
  id uuid primary key default gen_random_uuid(),
  lead_id uuid references leads(id) not null,
  day int not null,
  channel text not null,     -- email | social | dm
  content text not null,
  sent boolean default false
);

-- content creation
create table content_items (
  id uuid primary key default gen_random_uuid(),
  company_id uuid references companies(id) not null,
  type text not null,        -- blog | social | caption | landing
  topic text,
  body text,
  status text default 'draft', -- draft | approved | published
  created_at timestamptz default now()
);

-- marketing & ads
create table campaigns (
  id uuid primary key default gen_random_uuid(),
  company_id uuid references companies(id) not null,
  goal text, budget numeric,
  channel_mix jsonb,
  ad_variants jsonb,
  created_at timestamptz default now()
);

Enable RLS on every table above. Write policies so all CRUD operations require
`companies.owner_id = auth.uid()` (directly on `companies`, and via a join/subquery on every
child table that references `company_id`). Double-check: a second user must never be able to
read the first user's rows. After creating the schema, write the equivalent SQL into
`/supabase/migrations/0001_init.sql` so it's version-controlled in the repo.
```

---

## PROMPT 3 — Auth

```
Implement Supabase email/password authentication:
- /app/(auth)/login/page.tsx and /app/(auth)/signup/page.tsx, styled per the design system
  described in Prompt 0 (cream card, navy text, blue primary button) — keep them simple, single
  form, one hero illustration beside it.
- /lib/supabase/client.ts and /lib/supabase/server.ts helpers using @supabase/ssr.
- Middleware that protects every route under /app/(app)/* and redirects unauthenticated users to
  /login.
- On first login, if the user has no row in `companies`, redirect them to an onboarding step that
  creates one (name, industry, ICP, brand voice — matches the schema from Prompt 2).
Confirm signup -> onboarding -> dashboard redirect works end to end before continuing.
```

---

## PROMPT 4 — Design system components

```
Before wiring any real data, build the reusable "Cofounder" design-system components in
/components/ui, using the color tokens and rules from Prompt 0. Add these Tailwind theme colors
to tailwind.config.ts first:

colors: {
  ink: "#14213D",
  paper: "#FDFCF7",
  card: "#F4F2EA",
  brandBlue: "#2E6FF2",
  brandBlueSoft: "#E4EDFF",
  brandGreen: "#3E8E5A",
  brandGreenSoft: "#E6F3EA",
  watchOut: "#F2A93B",
  watchOutSoft: "#FCEFDA",
}

Build these components:

1. <ChapterHero title subtitle eyebrow bullets illustration /> — full-width banner: small pill
   eyebrow label top-left, big two-line bold headline, one-sentence muted subtitle, up to 3
   bullet highlights, and a large rounded illustration panel below (uses <PixelIllustration>).

2. <CalloutCard variant="tip" | "watch" | "checklist"> — tip = light blue bg "AGENT TIP" label;
   watch = light amber bg "WATCH OUT" label; checklist = cream bg with a list of items, each with
   a circular bullet that animates fill (scale 0.8→1 + color) when `done` is true. Must accept
   real props, not hardcoded text.

3. <StepDiagram steps=[{title, description}] /> — numbered circles connected by a horizontal
   line, each with a title + one-line description underneath. Reusable for the Coordinator
   routing pipeline and the sales outreach cadence.

4. <StatFunnel stages=[{label, percent}] /> — horizontal bars of decreasing width with a %
   label on the left, like a conversion funnel.

5. <PixelIllustration name="rocket" | "robots" | "satellite" | "train" /> — generate these as
   flat, geometric pixel-block SVGs with a 2–3 color sky-gradient background (blues/oranges),
   inline in the component (no external image files needed unless easier). Keep them simple flat
   shapes, not photorealistic.

6. <AgentCard agent icon status /> — used on the Dashboard grid, one per specialist agent, shows
   a short description and a "running / idle" status pill.

7. <ChatBar onSubmit placeholder /> — the Coordinator's natural-language input bar, with a
   pulsing "●●●" thinking indicator (brandBlue dots) while awaiting a response — not a generic
   spinner.

8. <ActivityItem agent instruction summary timestamp /> — one row in the Activity timeline.

Add Framer Motion entrance animation (fade + y:12→0, 300–400ms, 60ms stagger across children) as
a shared wrapper `<Reveal>` component and use it around major page sections.

Build a small style-guide page at /app/(app)/style-guide/page.tsx that renders every component
with placeholder data so we can visually verify before wiring real logic. Show me this page is
rendering correctly before moving to the next prompt.
```

---

## PROMPT 5 — Agent functions (backend logic, no UI yet)

```
Implement the five specialist agents plus the Coordinator in /lib/agents, all conforming to the
shared contract from Prompt 0:

  type AgentInput = { companyId: string; instruction: string; context?: Record<string, unknown> };
  type AgentResult = { summary: string; data?: Record<string, unknown>; logEntry: string };

Each agent calls the Anthropic API (POST https://api.anthropic.com/v1/messages, model
claude-sonnet-4-6, max_tokens 1000, ANTHROPIC_API_KEY from env) with a task-specific system
prompt, then persists structured results to Supabase using the service-role client (server-side
only).

1. /lib/agents/customerSupport.ts
   - Input: a customer message (+ optional ticket id).
   - Before calling Claude, fetch any existing support_tickets/company context as lightweight
     retrieval (simple keyword match is fine — no need for a vector DB).
   - Ask Claude to draft a reply + classify a tag (billing | bug | onboarding | other) + decide an
     escalation flag if it's not confident. Require strict JSON output from the model.
   - Insert/update a `support_tickets` row. Return a one-sentence summary.

2. /lib/agents/salesOutreach.ts
   - Input: an ICP description + one or more lead names/companies.
   - Ask Claude to write a personalized cold email + a 4–5 day follow-up cadence (mirrors: Day 1
     email, Day 2 social touch, Day 3 email, Day 4 social touch, Day 5 email) and a Tier 1/2/3
     score with one-line reasoning. Strict JSON output.
   - Insert a `leads` row (or update if it already exists) + insert `sequences` rows per day.

3. /lib/agents/contentCreation.ts
   - Input: content type (blog | social | caption | landing), topic, and the company's
     brand_voice from `companies`.
   - Ask Claude to draft the content in that brand voice. Insert a `content_items` row with
     status 'draft'.

4. /lib/agents/marketingAds.ts
   - Input: budget, target audience description, goal (awareness | signups | sales).
   - Ask Claude for: a suggested channel mix (as JSON: channel -> % of budget), 2–3 ad copy
     variants, and short targeting suggestions. Insert a `campaigns` row.

5. /lib/agents/analytics.ts
   - No LLM-required inputs — this agent's job is to read real Supabase rows for a company:
     count of leads by stage, tickets by status/tag, content by status, campaigns and their
     budgets, and activity_log volume by agent over the last 7/30 days.
   - Feed those real numbers to Claude and ask for a short natural-language summary
     ("This week: 12 leads contacted, 3 replies, 40% ticket auto-resolution rate...").
   - Return both the numeric data (for charts) and the summary text. Do not let Claude invent
     numbers — only summarize what you computed from the DB.

6. /lib/agents/coordinator.ts
   - Exports `runCoordinator(companyId, message)`.
   - First calls Claude with a classification-only system prompt that must return strict JSON:
     { "agent": "sales_outreach"|"customer_support"|"content_creation"|"marketing_ads"|"analytics"|"multi",
       "reasoning": "short reason",
       "subtasks": [ { "agent": "...", "instruction": "..." } ] }
   - For each subtask, call the matching agent function, then insert an `activity_log` row
     (agent, instruction, summary).
   - If more than one subtask ran, make one more short Claude call to synthesize their summaries
     into a single founder-facing response. Otherwise return the single agent's summary directly.
   - Always strip markdown code fences before JSON.parse, and wrap every Claude call in
     try/catch with a sane fallback message on failure — never let a parsing error surface as a
     raw crash to the user.

Write a short /scripts/testAgents.ts that calls each agent function directly with sample input
and logs the result, so we can verify the backend works via `npx tsx scripts/testAgents.ts`
before building any UI on top of it.
```

---

## PROMPT 6 — API routes

```
Create Next.js Route Handlers that wrap the agent functions from Prompt 5:

  POST /app/api/coordinator/route.ts        { companyId, message } -> { synthesis, results }
  POST /app/api/agents/support/route.ts     -> runs customerSupport directly
  POST /app/api/agents/sales/route.ts       -> runs salesOutreach directly
  POST /app/api/agents/content/route.ts     -> runs contentCreation directly
  POST /app/api/agents/marketing/route.ts   -> runs marketingAds directly
  GET  /app/api/agents/analytics/route.ts   -> runs analytics, returns KPIs + summary
  GET  /app/api/activity/route.ts           -> paginated activity_log rows for a company

Every route must:
1. Read the authenticated user from the Supabase server client (reject with 401 if none).
2. Validate the request body with zod.
3. Confirm the authenticated user owns the given companyId (query companies.owner_id) before
   doing anything else — reject with 403 otherwise.
4. Call the relevant agent function, return its result as JSON, and let any Supabase writes the
   agent already performed stand as the source of truth (routes are thin wrappers, not where
   business logic lives).

After building these, test each one with curl or a REST client against the dev server and paste
me the request/response for at least the coordinator route and one specialist route before we
move on to frontend wiring.
```

---

## PROMPT 7 — Frontend pages

```
Build these pages, in this order, using the Prompt 4 design-system components and wiring real
data through the Prompt 6 API routes:

1. /app/(marketing)/page.tsx — public landing page. ChapterHero with the product's one-line
   pitch ("A dashboard where a founder types what they need and a Coordinator Agent routes it to
   the right specialist"), a short "how it works" 3-step section using <StepDiagram>, an
   illustration, and a CTA to sign up. Cofounder-styled top nav (logo pill + How it works /
   Agents / Pricing-style links, even if some are placeholders).

2. /app/(app)/dashboard/page.tsx — the demo centerpiece. Top: <ChapterHero> welcoming the
   founder by company name. Middle: a grid of 5 <AgentCard>s (one per specialist), each linking
   to its own page. A prominent <ChatBar> for talking to the Coordinator, showing the pulsing
   thinking state while awaiting /api/coordinator, then rendering the synthesis response and
   which agents ran. Sidebar: recent <ActivityItem> feed (last 5) + a <CalloutCard variant="tip">
   with a sample prompt suggestion.

3. /app/(app)/agents/support/page.tsx — ticket inbox (list of support_tickets with tag/status
   badges) + a form to submit a new customer message, which calls /api/agents/support and shows
   the AI-drafted reply + tag + escalation flag.

4. /app/(app)/agents/sales/page.tsx — lead table (name, company, tier, stage) + an add-lead form
   (name/company/email + ICP text) that calls /api/agents/sales, plus a <StepDiagram> rendering
   the generated day-by-day cadence for a selected lead.

5. /app/(app)/agents/content/page.tsx — a generator form (type/topic) that calls
   /api/agents/content, and a simple kanban of content_items grouped by status
   (draft/approved/published) with drag-free status-change buttons.

6. /app/(app)/agents/marketing/page.tsx — campaign builder form (budget/audience/goal) calling
   /api/agents/marketing, rendering the returned channel mix as a small bar/pie (Recharts) and
   the ad copy variants as cards.

7. /app/(app)/agents/analytics/page.tsx — KPI cards (leads, tickets, content, campaigns counts),
   a <StatFunnel> for lead stage progression, a Recharts line/bar chart of activity_log volume
   over time, and the AI-generated natural-language summary from /api/agents/analytics.

8. /app/(app)/activity/page.tsx — full timeline of activity_log, filterable by agent, paginated.

9. /app/(app)/settings/page.tsx — edit company name/industry/icp/brand_voice.

Every page needs a designed empty state (a <PixelIllustration> + one-line prompt like "No leads
yet — try asking the Coordinator: 'Find me leads for independent dental practices'") — never show
a bare blank page. Wrap each page's main sections in <Reveal> for the entrance animation.
```

---

## PROMPT 8 — Seed data + polish for demo

```
Write /scripts/seed.ts that, given a company id, inserts realistic sample data: 6–8 leads across
different stages/tiers with sequences, 5–6 support tickets in different states, 4–5 content items
across draft/approved/published, 2 campaigns, and a matching spread of activity_log rows with
timestamps over the last 14 days so the Analytics charts have something meaningful to show. Run
it once against a demo company and confirm every page (Dashboard, each Agent page, Analytics,
Activity) looks intentional and populated — a live demo on an empty database looks bad.

Then do a final visual pass:
- Confirm the pixel illustrations render on Dashboard hero, each Agent landing panel, Analytics
  page, and all empty states.
- Confirm Framer Motion entrance animations run on every page without jank.
- Confirm the ChatBar's thinking state animation looks like on-brand pulsing dots, not a generic
  spinner.
- Confirm mobile responsiveness on the Dashboard and at least one Agent page.
```

---

## PROMPT 9 — Testing & security checklist

```
Run through and confirm each of the following, fixing anything that fails:

- [ ] Coordinator correctly routes at least 5 distinct sample prompts to the right agent(s) —
      write these as a fixed test list in /scripts/testCoordinator.ts and show me the output.
- [ ] Each specialist agent works when called directly via its own page, not only via Coordinator.
- [ ] RLS confirmed: create a second test user/company and verify it cannot see the first
      company's leads, tickets, content, campaigns, or activity log — via the Supabase dashboard
      or a direct query test, not just the UI.
- [ ] Every page has a designed empty state.
- [ ] Activity log updates within a couple seconds of any agent action (no manual refresh needed,
      or a lightweight polling/subscription confirms this works).
- [ ] Analytics numbers match real row counts in Supabase (spot-check by querying directly).
- [ ] No secrets committed; `.env.local` is gitignored; confirm with `git status`.
```

---

## PROMPT 10 — Deploy

```
1. git init, commit everything, push to a new GitHub repo.
2. Import the repo into Vercel.
3. Set the same environment variables from .env.local.example in the Vercel project settings
   (NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY,
   ANTHROPIC_API_KEY).
4. Deploy, then re-run the Prompt 9 checklist against the live production URL, not just
   localhost — check auth, RLS, agent calls, and analytics all work in production.
5. Give me the final production URL and a short summary of anything that behaved differently in
   production vs. local dev.
```

---

## Appendix A — Mapping to the SPIT mini-project rubric

| Rubric item | Where it's satisfied |
|---|---|
| Problem Definition / Novelty | Multi-agent coordination (Coordinator + 5 specialists) vs. a single general-purpose assistant |
| Technical Competency | Real agent contracts (Prompt 5), Postgres schema with RLS (Prompt 2), routing logic (coordinator.ts) |
| Work Done / Implementation | Prompts 1–8 are individually checkable, demoable progress you can screenshot for each phase |
| Presentation | The Cofounder-cloned design system (Prompt 4) makes the demo look like a real shipped product, not a prototype |
| Report citations | Cite the Anthropic API docs, Supabase docs, Next.js docs, and include screenshots of your `<StepDiagram>` architecture diagrams as figures |

## Appendix B — Suggested timeline

**Phase 1 (survey / problem definition / planning):** Prompts 0–2 — finalize architecture,
schema, and get the clickable design-system-only prototype (Prompt 4's style guide page) working
with mock data.

**Phase 2 (design / dev / testing):** Prompts 3–10 — real auth, real agents, wired frontend,
seeded demo data, tested, deployed.

---

*End of build prompt. Paste Prompt 0 first as pinned context, then Prompts 1 through 10 one at a
time into Antigravity, confirming each step works before moving to the next.*
