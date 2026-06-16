# UiPath Product Feedback — Building a Multi-Agent Crisis Orchestration on Maestro Case

*From a team that shipped a real, end-to-end solution on Automation Cloud (AgentHack 2026, Track 1). Names below are fictional; this is constructive feedback from power users who ran the platform hard for ~5 weeks.*

---

## Overall experience

We built a single, living **three-level nested Maestro Case** that orchestrates a multi-stakeholder healthcare-payment cyber crisis end to end: a master crisis case fans out to ~9 per-stakeholder parent cases and ~12 per-obligation grandchild cases, driven by five mid-flight goal reversals across a simulated 90-day timeline. The solution spans **13 UiPath product surfaces** and **11 AI agents** (6 Agent Builder low-code reasoners on BYO Claude + 5 Coded Python agents, one implemented as a LangGraph `StateGraph` via `uipath-langchain`), with Context Grounding, Data Fabric, Integration Service API Workflows, Action Center HITL gates, the LLM Gateway/Trust Layer, and a Coded Web App command center. The platform genuinely supported this scale: the case canvas really did act as the orchestrator. The friction we hit was almost entirely at the **Maestro Case** authoring/runtime edges and a few cross-product status/ingestion seams — detailed below with error codes and dates.

---

## What worked well

- **Native case nesting as a first-class construct.** Wiring three `caseplan.json` definitions via the `case-management` task type to get master → parent → grandchild nesting worked, and the Reversal-3 fan-out (6 grandchild spawns on the canvas in one beat) is a genuinely strong visual and architectural story. Nothing else we evaluated models "one crisis, many evolving sub-cases" this directly.
- **Agent-as-task model.** Invoking agents as `type: "agent"` tasks inside stages — and mixing low-code Agent Builder agents with Coded Agents in the *same* case — is clean and composable. Being able to swap a deterministic Coded Agent for a LangGraph implementation of the same task without touching the canvas was a highlight.
- **LLM Gateway → Trust Layer uniformity.** Every LLM call (BYO Claude Sonnet 4.6 *and* first-party OpenAI advisory calls) flowing through one gateway with PHI/PII guardrails applied uniformly is exactly the governance posture a regulated-industry buyer wants. This "just worked" and is a real differentiator.
- **LangGraph interop via `uipath-langchain`.** A Coded Agent using an internal LangGraph `StateGraph`, deployed through `langgraph.json` + `uipath init` codegen, packed/published with `uip codedagent`, and then invoked as a normal case task — framework-agnostic agent layer with no special-casing on the canvas. This is a quietly excellent piece of design.
- **Context Grounding retrieval quality.** Once documents were in a supported format, retrieval against our bound corpus was accurate and fast, and binding an index to a specific Agent Builder agent is intuitive.
- **Data Fabric seeding via CLI.** `uip df` round-tripped a real dataset (9 entities, ~4,320 telemetry rows) reliably once we learned its field-naming rules. Seeding the whole demo dataset reproducibly from scripts was a real productivity win.

---

## Issues & bugs

| Area | What happened | Severity | Repro / evidence (error code + date) |
|---|---|---|---|
| Maestro Case — spawn inputs | `=datafabric.qem:` query expressions **fail at runtime** when used in case-spawn inputs (`JobArguments`), so per-spawn Data Fabric query-on-spawn is not usable. We had to pass **literal stakeholder slugs** into each spawn instead. | High | Error **400300** "Syntax error at index 4"; live-proven 2026-06-10 on package v1.0.21. |
| Maestro Case — task resilience | Maestro **Case** agent tasks expose **no element-level auto-retry** policy. The Studio Web properties panel for a case agent task shows only General / Entry rules / Implementation / Update variables — there is **no Error-handling section** (that section exists only on Maestro **Process/BPMN** task elements). Case resilience must be reconstructed from rework/re-entry + SLA escalation + operator `instance retry`. | High | Verified by direct Studio Web UI inspection of the `clearflow-master-crisis` caseplan, 2026-06-15. |
| Maestro Case — caseplan round-trip | Downloading/regenerating a caseplan from the Studio Web canvas **strips `metadata.caseAppConfig`** (it is UI-config only). Any CLI-side round-trip silently loses it, so we had to script restoration of `caseAppConfig` (and other root metadata) after every canvas regenerate. | Medium | Reproduced repeatedly; we ship a merge/restore script to re-inject it post-download. |
| Maestro Case — job/case status sync | A **Completed** Maestro Case instance **never flips its backing Orchestrator job to Successful** — the Jobs view shows "Running" indefinitely (we saw masters whose instances completed 1 and 3 days earlier still showing "Running" jobs). Source of truth is the Case Instances view, not Jobs. Cancelled instances *do* flip to Stopped, so the gap is specific to successful completion. | Medium | Live-proven 2026-06-12; we had to write a janitor to sweep zombie "Running" rows before judging. |
| Context Grounding — ingestion | CG ingestion **silently skips `.md` files** — ingestion reports *Successful*, but search returns 0 hits. Only `.txt` (and other supported types) actually index. No error or skipped-file warning is surfaced anywhere. We lost time before realizing our Markdown corpus was never searchable. | Medium | Discovered 2026-06-12; resolved only by converting the corpus to `.txt`. |
| Action Center — HITL gate handling | **Deleting** a pending HITL gate task in Action Center (instead of Approve/Deny or File/Withdraw) **faults the backing case instance**. This is arguably correct as an audit signal, but it is surprising and there's no guard or confirmation. | Medium | Error **160009**, `IncidentType "User"`, pinned to the gate element; live-proven 2026-06-15 (5 deleted grandchild gates → Faulted; the one actioned → Completed). |
| AppTask completion — docs/API | The AppTask completion endpoint is effectively **undocumented**. Hitting the obvious-looking routes returned **405**; the correct route is `POST /tasks/AppTasks/CompleteAppTask`. Until we found it, programmatic completion looked impossible (it appeared SPA/click-only). | Low | 405 on wrong endpoints; resolved 2026-06-14 once the real route was identified (now wrapped by `uip tasks complete --type AppTask`). |
| Coded App — deploy CLI | `uip codedapp deploy` with `-v` / `--path-name` **hangs forever** on "still being indexed" and never returns. The **bare** `deploy -n <name> --folder-key <key>` form completes normally. | Low | Reproduced consistently; documented as the required workaround in our deploy runbook. |
| Studio Web — authoring UX | A task write-back "Update variables" mapping that omits the internal `originalVar` marker triggers a **false** "The referenced variable may have been removed" warning, even though the variable **is** declared and runtime is unaffected. Re-picking the variable in the mapping clears it. | Low | Observed on `clearflow_vector_status` write-back, 2026-06-15 (variable declared, runtime fine). *Evidence: authoring-session notes; warning is cosmetic, not a runtime defect.* |

---

## Feature requests

1. **Case-task-level retry policy.** Add an element-level (or stage-level) auto-retry/error-handling policy to Maestro **Case** agent tasks, matching what BPMN process tasks already offer. Today case resilience must be hand-assembled from rework rules + SLA escalation + operator `instance retry`; a declarative retry policy on the task would close the gap.
2. **`qem:` (Data Fabric query) support in case-spawn inputs.** Make `=datafabric.qem:` expressions evaluate correctly in spawn `JobArguments` so fan-out can be data-driven instead of forcing literal slugs. At minimum, fail at design/validation time with a clear message rather than at runtime with **400300**.
3. **Preserve `caseAppConfig` (and root metadata) on canvas round-trip.** A canvas download/regenerate should not strip UI-config metadata. Either persist it through the round-trip or emit an explicit warning naming what was dropped, so teams aren't silently losing config.
4. **Context Grounding: ingest non-`.txt` (e.g. `.md`) or warn on skip.** Either extend ingestion to common doc formats like Markdown, **or** surface a per-file "skipped (unsupported type)" warning instead of reporting *Successful* while indexing nothing. Silent zero-result corpora are a sharp edge.
5. **Job/case status sync.** Reconcile a Completed Maestro Case instance with its backing Orchestrator job so the Jobs view reflects completion (or clearly mark case-backed jobs as "managed by Case — see Case Instances"). The current "Running forever" state makes a healthy tenant look broken.
6. **Confirm-on-destroy for HITL gate tasks.** When an operator deletes (rather than actions) a pending gate task, prompt for confirmation — or offer a distinct "cancel/withdraw" action — so an accidental delete doesn't fault a live case (**160009**) without warning.
7. **Document the AppTask completion API.** Publish `POST /tasks/AppTasks/CompleteAppTask` (and the `--type AppTask` CLI path) so teams don't burn time on 405s against the wrong endpoint.
8. **Fix the Coded App `deploy -v/--path-name` hang.** The "still being indexed" path should time out or stream progress instead of blocking indefinitely.

---

## Bottom line

UiPath Maestro Case + Agent Builder + Coded Agents (incl. LangGraph via `uipath-langchain`) + Context Grounding + Data Fabric let us build a genuinely ambitious three-level, multi-agent crisis orchestration entirely on Automation Cloud — the core composition model is excellent. The biggest wins for the next builder would be a **case-task retry policy**, **`qem:` support in spawn inputs**, **caseAppConfig round-trip preservation**, and a few **silent-failure → explicit-warning** fixes (Context Grounding skips, job/case status sync).
