# UiPath Product Feedback — Survey Responses

*Mapped 1:1 onto the **UiPath AgentHack (2026) — "What's your UiPath platform/product feedback?"** form. Fill the personal fields (1–4, 14) at submit time; the substantive answers (7–13) are ready to paste. Best Product Feedback award: $1,500.*

*Context: we built a real, end-to-end solution on Automation Cloud over ~5 weeks. Names in any narrative are fictional; the feedback is from power users who ran the platform hard.*

---

### 1. What's your first name?

`[your first name]`

### 2. What's your last (family) name?

`[your last name]`

### 3. What's the name of your team? (Solo: the name you chose or your name again.)

`[your team name]`

### 4. Add here your email address.

`puneetsatyawan@gmail.com`

### 5. Please rate your overall satisfaction with UiPath AgentHack.

`[rating]` — recommend the top rating; the event let us build something genuinely ambitious end-to-end.

### 6. Which of the following categories did you compete in AgentHack?

☑ **UiPath Maestro Case**
☐ UiPath Maestro BPMN
☐ UiPath Test Cloud

*(We also used Maestro BPMN sub-flows under case stages, but our primary track is Maestro Case — "Best of Maestro Case".)*

### 7. Please briefly describe your use case.

We built a single, living **three-level nested Maestro Case** that orchestrates a multi-stakeholder healthcare-payment cyber crisis end to end. A master crisis case fans out to ~9 per-stakeholder parent cases and ~12 per-obligation grandchild cases, driven by five mid-flight goal reversals across a simulated 90-day timeline. The hero beat: Reversal 3 fans out 6 grandchild spawns on the canvas in a single moment.

The solution spans **13 UiPath product surfaces** and **12 AI agents** — 6 Agent Builder low-code reasoners on BYO Claude + 6 Coded Python agents (two implemented as LangGraph `StateGraph` agents via `uipath-langchain`) — with Context Grounding, Data Fabric, Integration Service API Workflows, Action Center HITL gates, the LLM Gateway / Trust Layer, and a Coded Web App command center. The Maestro Case canvas itself is the orchestrator.

### 8. Please indicate your overall satisfaction with the UiPath Platform.

☑ **Very satisfied**

The core composition model — Maestro Case + Agent Builder + Coded Agents (incl. LangGraph via `uipath-langchain`) + Context Grounding + Data Fabric — let us build a genuinely ambitious three-level, multi-agent orchestration entirely on Automation Cloud. The platform supported this scale; the case canvas really did act as the orchestrator.

### 9. How easy was it to build your solution?

☑ **Somewhat difficult**

The composition model is excellent and much of it "just worked," but we hit real friction at the **Maestro Case** authoring/runtime edges and a few cross-product status/ingestion seams (detailed in Q10). Most of those cost us time mainly because the failures were silent rather than surfaced.

### 10. What challenges (if any) did you encounter while building the solution?

Concrete issues, with error codes and dates:

1. **`=datafabric.qem:` query expressions fail at runtime in case-spawn inputs** (`JobArguments`) — Error **400300** "Syntax error at index 4", live-proven 2026-06-10 on v1.0.21. Per-spawn Data-Fabric-query-on-spawn isn't usable; we had to pass literal stakeholder slugs into each spawn instead. *Ask: evaluate `qem:` correctly in spawn inputs, or at least fail at design/validation time with a clear message instead of at runtime.*

2. **Maestro Case agent tasks expose no element-level auto-retry policy.** The Studio Web properties panel for a case agent task shows only General / Entry rules / Implementation / Update variables — there is no Error-handling section (that exists only on Maestro **Process/BPMN** task elements). Case resilience had to be reconstructed from rework/re-entry + SLA escalation + operator `instance retry`. Verified by direct Studio Web inspection of the `clearflow-master-crisis` caseplan, 2026-06-15. *Ask: add a declarative element/stage-level retry policy to case agent tasks, matching BPMN tasks.*

3. **Canvas round-trip strips `metadata.caseAppConfig`.** Downloading/regenerating a caseplan from the Studio Web canvas silently drops `caseAppConfig` (it's UI-config only), so any CLI-side round-trip loses it. We had to script restoration after every regenerate. *Ask: persist it through the round-trip, or emit an explicit warning naming what was dropped.*

4. **A Completed Maestro Case instance never flips its backing Orchestrator job to Successful.** The Jobs view shows "Running" indefinitely (we saw masters whose instances completed 1–3 days earlier still showing "Running"). Cancelled instances *do* flip to Stopped, so the gap is specific to successful completion. Source of truth is the Case Instances view, not Jobs — but the stale rows make a healthy tenant look broken. We had to write a janitor to sweep zombie rows before judging. Live-proven 2026-06-12.

5. **Context Grounding silently skips `.md` files.** Ingestion reports *Successful*, but search returns 0 hits — only `.txt` (and other supported types) actually index. No error or skipped-file warning anywhere. We lost time before realizing our Markdown corpus was never searchable. Discovered 2026-06-12; resolved only by converting to `.txt`.

6. **Deleting a pending HITL gate task in Action Center faults the backing case instance** (Error **160009**, `IncidentType "User"`, pinned to the gate element; live-proven 2026-06-15 — 5 deleted grandchild gates → Faulted, the one actioned → Completed). Arguably correct as an audit signal, but surprising and with no guard or confirmation. *Ask: confirm-on-destroy, or a distinct "cancel/withdraw" action.*

7. **The AppTask completion endpoint is effectively undocumented.** Obvious-looking routes returned **405**; the correct route is `POST /tasks/AppTasks/CompleteAppTask`. Until we found it, programmatic completion looked impossible (it appeared SPA/click-only). Resolved 2026-06-14 (now wrapped by `uip tasks complete --type AppTask`). *Ask: document it.*

8. **`uip codedapp deploy` with `-v` / `--path-name` hangs forever** on "still being indexed" and never returns; the bare `deploy -n <name> --folder-key <key>` form completes normally. Reproduced consistently. *Ask: time out or stream progress instead of blocking indefinitely.*

9. **False "variable may have been removed" warning** in Studio Web: a task write-back "Update variables" mapping that omits the internal `originalVar` marker triggers the warning even though the variable is declared and runtime is unaffected. Re-picking the variable clears it. Cosmetic, observed on `clearflow_vector_status` write-back, 2026-06-15.

### 11. If you had to change one thing about the UiPath Platform experience, what would it be and why?

**Turn silent failures into explicit warnings.** Our single biggest time sink was not the platform's limits but its *quiet* ones — Context Grounding reporting "Successful" while indexing nothing (`.md` skipped), the canvas dropping `caseAppConfig` on round-trip with no notice, `qem:` expressions failing only at runtime instead of validation time, and Completed case instances leaving "Running" jobs behind. Each was individually small but expensive to diagnose because nothing surfaced the problem. A consistent "we skipped / dropped / couldn't evaluate X, here's why" signal across ingestion, canvas round-trip, and spawn-input validation would have saved us days and would make the platform feel far more trustworthy to a regulated-industry buyer.

### 12. What surprised you the most about building with UiPath during AgentHack? What would you tell another developer trying it for the first time?

**Most surprising (in a good way):** the **agent-as-task** model and **LangGraph interop**. Invoking agents as `type: "agent"` tasks inside case stages — and mixing low-code Agent Builder agents with Coded Python agents in the *same* case — is genuinely clean and composable. We swapped a deterministic Coded Agent for a LangGraph `StateGraph` implementation of the same task (via `langgraph.json` + `uipath init` codegen, packed/published with `uip codedagent`) and invoked it as a normal case task with **zero special-casing on the canvas**. A framework-agnostic agent layer like that is a quietly excellent piece of design. The **LLM Gateway → Trust Layer** uniformity (every BYO-Claude *and* first-party LLM call flowing through one gateway with PHI/PII guardrails applied uniformly) also just worked, and is exactly the governance posture a regulated buyer wants.

**What I'd tell a first-timer:** Lean into native case nesting — wiring multiple `caseplan.json` definitions via the `case-management` task type to get master → parent → grandchild nesting is the real superpower, and nothing else models "one crisis, many evolving sub-cases" this directly. But treat the **Case Instances view as your source of truth** (not the Jobs view), keep your Context Grounding corpus in `.txt`, script a restore step for `caseAppConfig` after any canvas round-trip, and pass **literal values** into spawn inputs rather than `qem:` queries. Knowing those four things up front would have saved us most of our lost time.

### 13. UiPath Maestro orchestrates AI agents, RPA, APIs, and people across one end-to-end process. What did you build with Maestro that would have been a mess to stitch together without it?

A **three-level nested, multi-agent crisis orchestration** that, without Maestro, would have been an unmanageable tangle of custom queues, state machines, and glue code. Maestro Case held it together as **one living process**: a master crisis case spawning ~9 stakeholder parent cases and ~12 obligation grandchild cases (Reversal 3 fanning out 6 grandchildren on the canvas in a single beat), with **12 AI agents** (low-code + coded, including LangGraph) invoked as ordinary case tasks alongside **Integration Service API Workflows** (~13 mock external systems), **Action Center HITL approval gates** where humans approve fiduciary decisions mid-flow, and **Data Fabric** as the shared evidence ledger — all governed uniformly through the **LLM Gateway / Trust Layer**.

The hard part Maestro made easy: keeping agents, RPA-style API calls, and human approvals **coherent across five mid-flight goal reversals over a 90-day simulated timeline**, where each reversal re-shapes live sub-cases. Stitching that together by hand — agent orchestration, per-stakeholder fan-out, human approval routing, shared state, and guardrails — would have meant building our own case-management engine. The canvas *was* the orchestrator, so we built the crisis logic instead of the plumbing.

### 14. Can we share your story?

`[choose one]`
- ☐ Yes — use my name, title, and company in UiPath marketing materials
- ☐ Yes — but show me the final version before publishing
- ☐ Use my story without my name (anonymous attribution)
- ☐ No — keep this private for the UiPath team's internal reference only

---

## Appendix — issues at a glance

| # | Area | What happened | Severity | Evidence (code + date) |
|---|---|---|---|---|
| 1 | Maestro Case — spawn inputs | `=datafabric.qem:` fails at runtime in spawn `JobArguments`; forced literal slugs | High | **400300** "Syntax error at index 4"; 2026-06-10, v1.0.21 |
| 2 | Maestro Case — task resilience | No element-level auto-retry on case agent tasks (BPMN-only) | High | Studio Web inspection of `clearflow-master-crisis`, 2026-06-15 |
| 3 | Maestro Case — round-trip | Canvas download strips `metadata.caseAppConfig` | Medium | Reproduced repeatedly; ship a restore script |
| 4 | Job/case status sync | Completed case instance leaves Orchestrator job "Running" forever | Medium | Live-proven 2026-06-12; janitor sweep required |
| 5 | Context Grounding — ingestion | `.md` silently skipped; reports Successful, 0 hits | Medium | 2026-06-12; fixed by converting to `.txt` |
| 6 | Action Center — HITL | Deleting a pending gate task faults the case | Medium | **160009**, `IncidentType User`; 2026-06-15 |
| 7 | AppTask completion — docs | Endpoint undocumented; 405s until `POST /tasks/AppTasks/CompleteAppTask` found | Low | 405s; resolved 2026-06-14 |
| 8 | Coded App — deploy CLI | `deploy -v/--path-name` hangs on "still being indexed" | Low | Consistent; bare-form workaround |
| 9 | Studio Web — authoring UX | False "variable removed" warning when mapping omits `originalVar` | Low | `clearflow_vector_status` write-back, 2026-06-15 (cosmetic) |
