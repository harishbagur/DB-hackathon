# DB-hackathon
AI-powered Incident resolution
multi-agent-incident-resolution_1
Autonomous Incident Resolution — Multi-Agent System for ServiceNow
Global Hausbank HackathonTheme: Powering the European Champion with AI
Track: Operations & Efficiency
1. The Problem
Production support today is manual and repetitive.
An incident lands in ServiceNow. An engineer picks it up, reads it, searches for similar past incidents, hunts for a KB article, logs onto the server, runs a few diagnostic commands, and usually applies a fix that someone else has already applied fifty times before.
Three things are wrong with this:
Problem
Impact
A large share of incidents are false positives
Engineers spend time on tickets that needed no action
Most real incidents are repeat patterns
The same fix is rediscovered again and again
Knowledge stays in engineers' heads
Nothing is written down, so nothing gets faster
The result is high mean-time-to-resolve, engineer fatigue on low-value work, and no compounding improvement.
2. The Idea in One Sentence
A team of specialised AI agents that watches ServiceNow incidents, filters out the noise, fixes what it safely can, guides the user through what it can't, and writes down what it learns — so the system gets faster every week.
3. Why Multi-Agent Instead of One Big AI
A single model doing everything is hard to control, hard to audit, and hard to explain to a risk committee.
Splitting the work gives us:
Separation of duties — the agent that decides what to do is not the agent that does it
Least privilege — the Unix agent only ever gets Unix credentials
Auditability — every action is attributed to a named agent with a stated reason
Swappability — improve one agent without touching the rest
This mirrors how a real support team is structured: a triage lead, an automation tier, a service desk, and platform specialists.
4. The Agents
#
Agent
Job
Talks to
1
Triage Agent
Reads new incidents. Decides real vs false. Assigns confidence.
ServiceNow
2
Orchestrator
Deterministic router. Decides who handles the incident next. Enforces guardrails.
All agents
3
Self-Healing Agent
Matches incident to a known playbook and executes it.
Windows / Unix agents
4
Windows Agent
Executes commands and scripts on Windows servers.
Windows estate
5
Unix Agent
Executes commands and scripts on Unix/Linux servers.
Unix estate
6
Listener Agent
Conversational front door. Surfaces similar incidents and KB articles to the user.
User (via Teams / Virtual Agent)
7
Engineering Agent
Deep diagnosis when no playbook exists. Reasons over live server output.
Windows / Unix agents
8
Knowledge Agent
Turns every successful resolution into a draft KB article.
ServiceNow KB
Design note: Agents 1 and 2 are deliberately separate. Triage is an AI judgement call ("is this real?"). Orchestration is a rules engine ("given this state, who's next?"). Keeping the router deterministic makes the whole system predictable and much easier to defend.
5. The Flow
                    ┌─────────────────┐
   New incident ───▶│  TRIAGE AGENT   │
   in ServiceNow    │  real or false? │
                    └────────┬────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
         FALSE POSITIVE                   REAL
              │                             │
              ▼                             ▼
      ┌───────────────┐            ┌─────────────────┐
      │ Confidence?   │            │  ORCHESTRATOR   │
      │ >.85 auto-    │            │  route by CI +  │
      │   close       │            │  check guards   │
      │ .6-.85 down-  │            └────────┬────────┘
      │   grade       │                     │
      │ <.6 treat as  │                     ▼
      │   real ───────┼──────────▶ ┌─────────────────┐
      └───────────────┘            │  SELF-HEALING   │
                                   │  known playbook?│
                                   └────────┬────────┘
                                            │
                            ┌───────────────┴──────────────┐
                          YES                             NO
                            │                              │
                            ▼                              ▼
                  ┌──────────────────┐          ┌──────────────────┐
                  │ Execute via      │          │ LISTENER AGENT   │
                  │ Windows / Unix   │          │ opens chat with  │
                  │ agent            │          │ the user         │
                  └────────┬─────────┘          └────────┬─────────┘
                           │                             │
                      Verify fix                   Show top 10 similar
                           │                       incidents + KB
                    ┌──────┴──────┐                      │
                  WORKED       FAILED             ┌───────┴────────┐
                    │             │           RESOLVED        NOT RESOLVED
                    ▼             ▼               │                │
              ┌──────────┐   back to              │                ▼
              │ Close +  │   Orchestrator         │      ┌──────────────────┐
              │ KNOWLEDGE│   (hop count++)        │      │ ENGINEERING AGENT│
              │  AGENT   │                        │      │ live diagnosis   │
              └──────────┘                        │      └────────┬─────────┘
                                                  │               │
                                                  │      ┌────────┴────────┐
                                                  │    FIXED          STUCK
                                                  │      │                │
                                                  ▼      ▼                ▼
                                            ┌──────────────┐    ┌──────────────┐
                                            │  KNOWLEDGE   │    │ ESCALATE to  │
                                            │    AGENT     │    │ human (from  │
                                            │ draft KB     │    │ SNOW group)  │
                                            └──────────────┘    └──────────────┘
​
6. Step by Step
Step 1 — Triage
The Triage Agent picks up new incidents and classifies them.
It looks at the description, the affected configuration item (CI), the alert source, recent history on the same CI, and whether the condition has already self-corrected.
It returns a classification and a confidence score.
If FALSE POSITIVE:
Confidence
Action
Above 0.85
Auto-close with a reason code and a work note explaining the reasoning
0.60 – 0.85
Downgrade priority, add a work note, leave open for a human to confirm
Below 0.60
Do not trust the classification — treat as real and continue
We deliberately do not write back to monitoring configuration to suppress the alert rule. That is a separate integration with its own security review. Instead the system tags false positives with a pattern ID, so a weekly report shows which alert rules are generating the most noise — the humans decide what to change.
If REAL: hand to the Orchestrator.
Step 2 — Orchestrate
The Orchestrator is a rules engine, not a model. It:
Reads the CI record to find the platform (Windows or Unix) and criticality tier
Checks the guardrails (see section 8)
Increments the hop count
Routes to the next agent
If hop count exceeds 3, or 20 minutes have elapsed, it escalates to a human regardless of state. This is what stops agents ping-ponging an incident between each other forever.
Step 3 — Attempt Self-Healing
The Self-Healing Agent searches the playbook library for a match against the incident signature.
If it finds one above the confidence threshold, it dispatches execution to the platform agent — Windows Agent or Unix Agent — which holds the credentials and the script library for that estate.
After execution it verifies: it re-runs the diagnostic check that triggered the incident. A restarted service that immediately dies again is not a resolution.
Verified fixed → update ServiceNow, close, hand to Knowledge Agent
Failed or unverified → return to Orchestrator with the attempt logged
Step 4 — Engage the User
If no playbook applies, the Listener Agent opens a conversation with the affected user.
It presents:
The top 10 most similar historical incidents, each with how it was resolved
Matching KB articles
A plain-language summary of what the system already checked and ruled out
The user can act on a suggestion, or say none of it helps.
Delivery channel: Microsoft Teams bot or ServiceNow Virtual Agent — not an application installed on the user's machine. Endpoint software in a bank requires months of security review. Using an already-approved channel makes this deployable in reality, not just in a demo.
Step 5 — Deep Engineering
If the user isn't helped, the Engineering Agent takes over.
Unlike Self-Healing, which runs a known recipe, this agent reasons. It requests diagnostic output through the platform agent, reads it, forms a hypothesis, and requests more. It proposes fixes but does not execute anything above Tier 1 without approval.
Resolves it → Knowledge Agent writes it up
Cannot → escalate to a human from the assignment group on the ServiceNow record
Step 6 — Escalate to a Human
The Orchestrator reads the assignment group from the incident and pulls on-call membership.
The human joins the same conversation thread and inherits the full trail: everything attempted, all diagnostic output collected, the agent's working hypothesis. They do not start from zero.
Fallback: if the group is unstaffed or out of hours, route to the follow-the-sun group, then to the duty manager.
When the human resolves it, the Knowledge Agent captures that too — which is how the system learns from its own failures.
Step 7 — Capture Knowledge
Every resolution — automated, user-assisted, or human — produces a draft KB article.
The Knowledge Agent:
Checks for an existing near-duplicate article
If found, proposes an update to that article rather than a new one
If new, drafts it in the house KB format
Saves it in Draft state
A human approves before publish. Auto-publishing agent-written articles would pollute the knowledge base within weeks. The agent does the writing; a person does the signing off.
Approved articles feed straight back into the Listener Agent's search index, so the next occurrence resolves faster.
7. The Incident State Object
Every agent reads and writes one shared record. This is what stops context being lost at each handoff.
{
  "incident_id": "INC0012345",
  "classification": "real",
  "confidence": 0.91,
  "platform": "unix",
  "ci_criticality": "tier2",
  "current_owner": "self_healing_agent",
  "hop_count": 1,
  "actions_attempted": [
    {
      "agent": "self_healing_agent",
      "action": "restart_service:tomcat",
      "tier": 1,
      "outcome": "failed",
      "timestamp": "2026-07-23T09:14:02Z"
    }
  ],
  "diagnostics_collected": ["disk_usage", "service_status", "last_100_log_lines"],
  "hypothesis": "Disk full on /var causing service start failure",
  "escalation_reason": null
}
​
Stored as a JSON field on the ServiceNow incident record. Every write is mirrored into work notes in human-readable form, so the audit trail exists in ServiceNow itself and not only inside our system.
8. Guardrails
This is the section that matters most in a bank. Autonomy without controls is a non-starter.
Action tiers
Tier
Type of action
Who approves
0
Read-only — check disk, read logs, query service status
Nobody. Always allowed.
1
Low-risk, reversible — restart a service, clear a temp directory, rotate logs
Auto-execute, notify after
2
Configuration change, failover, restart on a critical CI
Human approves in chat before execution
3
Anything touching data, security, or a Tier-0 system
Human only. Agents advise, never act.
Pre-execution checks
Before any Tier 1+ action, the Orchestrator confirms:
Change window — is the CI inside a freeze period?
Criticality — a Tier-1 action on a Tier-0 CI is automatically promoted to Tier 2
Blast radius — how many downstream CIs depend on this one?
Rollback — is there a way back? If not, promote a tier.
Access control
Each agent has its own service account with the minimum permissions it needs
Credentials are pulled from a vault at execution time and never held in the agent
The Unix Agent cannot touch Windows and vice versa
No standing administrator rights anywhere
Audit
Every agent action writes to ServiceNow work notes: which agent, what it did, why it decided to, what came back. A reviewer can reconstruct the full decision path from ServiceNow alone.
Circuit breaker
If the automated resolution rate drops sharply or failed actions spike, the system stops acting and reverts to advisory-only mode until a human clears it.
9. Success Metrics
Metric
What it tells us
Mean time to resolve
The headline number
Auto-resolution rate
Share closed with no human involvement
False-positive suppression rate
Noise removed from the queue
Deflection rate
Resolved by the user through Listener without escalation
KB reuse rate
How often an agent-written article resolves a later incident
Verification failure rate
How often a "fix" didn't actually fix it — our honesty check
Escalation rate
Share reaching a human — should fall over time
Capture a baseline from historical ServiceNow data before the demo so improvement can be shown as a delta, not an assertion.
10. Demo Plan
Three scenarios, in this order. Each shows a different path through the system.
Scenario 1 — Noise removed.
A CPU spike alert that already self-corrected. Triage classifies it false with 0.93 confidence, auto-closes with a reason note. Ten seconds. Shows the filter working.
Scenario 2 — Self-healed.
Disk full on a Unix server. Triage says real, Orchestrator routes to Unix, Self-Healing matches the log-cleanup playbook, executes, verifies, closes. Knowledge Agent drafts the KB. Shows the happy path end to end.
Scenario 3 — Escalated with full context.
An unfamiliar application error. No playbook matches. Listener shows the user similar incidents — none help. Engineering Agent collects diagnostics, forms a hypothesis, hits a Tier 2 boundary and stops. Escalates to a human who arrives with the complete trail already assembled.
Scenario 3 is the most important one. It proves the system knows its own limits — which is exactly what a risk-conscious audience wants to see.
11. One-Day Build Plan
Given the timebox, build in this order and stop wherever the day ends. Everything above the line is a working demo.
Priority
Build
Why
P0
Triage Agent + false-positive handling
Scenario 1. Simplest, highest visible impact.
P0
State object + Orchestrator routing
Everything else depends on it. Keep it dumb.
P0
Self-Healing with 2–3 hardcoded playbooks
Scenario 2. Don't build a playbook engine — hardcode three.
P1
Listener Agent with similarity search over past incidents
Scenario 3 front half.
P1
Knowledge Agent drafting KB articles
Closes the learning loop visibly.
P2
Engineering Agent diagnostic loop
Scenario 3 back half. Can be scripted for the demo.
P2
Guardrail tier enforcement
Can be shown as a config table + one blocked action.
—
Everything below is roadmap, not build
P3
Alert correlation and deduplication
200 alerts → 1 incident
P3
Playbook auto-generation from resolved incidents
Self-expanding automation library
P3
Predictive mode — act before the incident is raised
The obvious next step
Shortcuts that are fine for one day:
Mock the ServiceNow API with a local JSON store if the sandbox is slow
Hardcode the three playbooks rather than building a library
Script the Engineering Agent's diagnostic sequence for the demo scenario
Skip the vault; use environment variables, but say in the presentation that production uses a vault
Shortcuts that are not fine:
Skipping verification after a fix — it's the difference between a demo and a toy
Auto-publishing KB articles without the draft state
Any action tier model at all is better than none
12. Roadmap Beyond the Hackathon
Near term — correlation agent to collapse alert storms; expand the playbook library from the top 20 recurring incident patterns; tune thresholds on real historical data.
Medium term — auto-generate playbooks from repeated Engineering Agent resolutions, so the automation library grows itself; extend to database and network estates.
Long term — shift from reactive to predictive: detect the pattern that precedes a known failure and act before the incident is raised. The end state is not faster incident resolution. It is fewer incidents.
Appendix — Design Decisions and Why
Decision
Reasoning
Triage separated from Orchestration
AI judgement and deterministic routing are different jobs. Mixing them makes the system unpredictable.
Orchestrator is a rules engine, not a model
Routing must be auditable and fast. No reason to spend an LLM call on an if-statement.
Similarity thresholds are a band, not 100%
Semantic matching never hits 100. Bands with a fallback are honest and workable.
Chat via Teams / Virtual Agent, not endpoint install
Endpoint software in a bank is a multi-month security review. This is deployable now.
KB drafts require human approval
Auto-publishing floods the knowledge base with unverified content.
Hop count and time limits
Without them, agents can pass an incident in circles indefinitely.
Verification step after every fix
Restarting a service that immediately crashes again is not a resolution.
False positives tagged, not suppressed at source
Writing to monitoring config is a separate integration and a separate risk conversation.
