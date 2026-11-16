# #5 · Real-Time Voice Agent (phone appointment booking)

> Prompt: "Design a phone agent for a clinic chain that answers calls, books/reschedules appointments, and transfers to a human when needed."

## §0 Assumptions
- 200 clinics · 20k calls/day · avg 3 min · peak 300 concurrent calls `(assume)`
- Voice-to-voice latency target: p50 < 800 ms, p95 < 1.5 s (human turn-taking feel)
- Booking writes to a scheduling system (EHR/PMS API); PHI → HIPAA-class controls
- Human transfer available 8–18h; after hours: message + callback
- Stack: telephony (Twilio/SIP) → media server → pipeline: STT (streaming) → LLM (ADK agent) → TTS (streaming); or Gemini Live API multimodal end-to-end. Postgres, Redis, Langfuse

## §1 Why an agent `[SW+AI]`
- Baseline: IVR menus ("press 2"). Breaks: callers say "I need to move my Tuesday thing to next week" — IVR can't parse; abandonment.
- Model adds: natural understanding, slot filling from messy speech, graceful repair ("did you say the 14th?").
- **L2 workflow + L3 step.** Booking is a state machine in code (`identify → intent → collect slots → confirm → write`). Model fills slots and phrases turns; agentic step = choosing tools (`find_slots`, `lookup_patient`) mid-dialog.
- Trigger: only the *dialog* is open-ended; the *transaction* is not. Keep the transaction in code.
- Cost of wrong: double-booked or wrong patient → confirm-before-write, read-back of date/time/name.
- **L5:** latency budget is the design; every choice (cascade vs end-to-end model, TTS chunking, barge-in) is a ms tradeoff; also PHI in audio → retention and redaction.

## §2 Crux
- **Sub-second turn-taking with correct transactions.** If it sounds laggy, callers hang up; if it books wrong, clinics revolt.
- Success points: streaming everywhere (STT partials → LLM → TTS chunks) · barge-in · deterministic booking state machine · explicit confirmation · warm transfer with context · call-level evals.
- Business metric: containment (booked without human) + abandonment rate; AI metric: slot accuracy + task success on call golden set.

## §3 NFR / BoE
| NFR | Target | Enforcer |
|---|---|---|
| Voice latency | p95 < 1.5 s (STT final 200 ms + LLM TTFT 400 ms + TTS first chunk 200 ms + network) | streaming, small model, warm connections |
| Availability | 99.95% during hours | multi-region media, breaker → IVR fallback |
| Booking correctness | 0 unconfirmed writes; idempotent | state machine + confirm + idem key |
| Concurrency | 300 calls; 1 pod ≈ 30 calls | autoscale on active-call metric |
| Cost | ≤ $0.15/call → $3k/day | STT/TTS minutes dominate; Flash for dialog |
| PHI | encrypted, retention 30 d audio / 1 y transcript, redaction | pipeline |
- Tokens small: ~2k in / 60 out per turn × 20 turns → 40k/call. Audio: 20k calls × 3 min = 60k min/day STT+TTS.

## §4 HLD
```
[SW] PSTN/Twilio --SIP/WebRTC--> [SW] Media server (per-call session, VAD, barge-in)
        |  audio frames                              ^ TTS audio chunks
        v                                           |
   [SW+AI] Call orchestrator (one process per call, asyncio):
      [AI] streaming STT (partials) -> [SW] turn detector (VAD + endpointing)
      -> [SW] dialog state machine (identify/intent/slots/confirm/write)
      -> [SW+AI] ADK LlmAgent (fills slots, phrases reply, picks tools) -> tools: lookup_patient | find_slots | book | reschedule(idem) | transfer
      -> [AI] streaming TTS
   [SW] Redis (live call state, 1 h) -> [SW] Postgres (calls, turns, transcripts, bookings, evals)
   [SW] Scheduling system API   [SW] Human agent (warm transfer w/ summary)   [SW+AI] Langfuse
```

## §5 Components — problem → design
- **Turn-taking `[SW+AI]`:** problem = when has the caller stopped? Design: VAD + endpointing (~500 ms silence, shorter after a question), speculative LLM start on STT partials, cancel on new speech. Barge-in: caller speech during TTS → stop TTS, mark reply as interrupted in transcript.
  - **L5:** the cascade (STT→LLM→TTS) is ~3 hops of latency; end-to-end speech models (Gemini Live) cut ~300 ms but reduce control over tools/state — choose cascade for transactional, E2E for conversational; keep the abstraction so you can swap.
- **Dialog state machine `[SW]`:** slots `{patient_id, intent, provider?, date, time}`; transitions in code; model output is structured (`{say, slot_updates, tool_call?}`) validated by schema; unknown state → clarify. Max 3 re-prompts per slot → transfer.
- **Booking write `[SW]`:** read back ("Tuesday the 14th at 3 pm with Dr. Lee, correct?") → explicit yes → `book(idem_key=call_id+slot)`; scheduling API idempotent; on ambiguous "yeah…no" → re-ask. Double-booking prevented by API's optimistic lock; conflict → offer next slot.
- **Live state `[SW]`:** per-call state in Redis with TTL; every turn appended to Postgres async; if the orchestrator pod dies, call re-routes to a new pod that loads Redis state and says "sorry, one moment" (< 3 s). Sticky routing by call_id.
- **Transfer `[SW+AI]`:** triggers: caller asks, 3 failed slot attempts, medical question, sentiment, tool failure. Warm transfer with a 3-line summary + collected slots pushed to agent screen; SIP REFER; if no agent in 60 s → voicemail + callback ticket.
- **Guardrails `[SW+AI]`:** no medical advice (classifier → transfer); PII read-back only for confirmation; prompt-injection surface small (caller speech) but tool outputs still wrapped; TTS output length cap (≤ 2 sentences) for latency.
- **Evals `[AI]`:** call golden set (200 recorded, consented, or synthetic TTS-generated caller scripts) replayed against the pipeline: slot accuracy, task success, latency percentiles; judge on politeness/repair; WER tracked per accent; CI replays 50 calls per change.
  - **L5:** synthetic caller simulator (LLM + TTS, noisy channel) enables load + regression tests at scale; measure interruptions/turn as a UX metric.

## §6 API / schema
- Telephony webhook `POST /calls/incoming` → media session; internal `POST /calls/{id}/transfer`; `GET /calls/{id}` (state, transcript)
- Model output contract: `{say: str, slots: {…}, tool: {name, args}?, end_call: bool}`
- `calls(id, clinic_id, from_hash, started, ended, outcome, transfer_reason)` · `turns(call_id, seq, speaker, text, audio_uri, latency_ms, interrupted)` · `bookings(call_id, idem_key UNIQUE, ext_id, status)` · `evals`

## §7 Hygiene
| Concern | Answer |
|---|---|
| AuthN | caller verified by DOB + phone match before PHI; tools scoped to clinic |
| Idempotency | booking idem key; STT/TTS stateless |
| Timeouts | LLM 3 s hard → filler phrase + retry; tool 2 s → "one moment" |
| Breaker | LLM down → scripted IVR + transfer; TTS down → prerecorded prompts |
| Backpressure | admission control: > pool capacity → queue message with ETA |
| Cache | slot availability cached 30 s; TTS cache for fixed phrases |
| Failover | multi-region media + Redis replication; RTO < 1 min |
| PII/PHI | audio encrypted, 30 d; transcripts redacted; BAA with vendors |

## §8 Failure → fallback
- LLM slow → filler ("let me check that") once, then transfer · STT garbage (WER spike) → ask to repeat, then transfer · Booking conflict → next slot · Pod dies → resume from Redis · Caller silent 10 s → prompt, then end politely.

## §9 Pop-up questions
1. **Why not end-to-end speech model?** — Less control over state/tools and confirmation; use for chit-chat, cascade for transactions; keep swappable.
2. **Where does the 1.5 s go?** — STT endpoint ~300, LLM TTFT ~400, TTS first chunk ~200, network ~200, buffer; speculative start hides STT.
3. **Caller interrupts mid-sentence?** — Barge-in via VAD; cancel TTS; mark interrupted; model gets partial context.
4. **Wrong patient booked?** — Identity verification before PHI; read-back confirm; idempotent write.
5. **Pod crash mid-call?** — Redis live state, sticky reroute, 3 s recovery phrase.
6. **How do you test?** — Replayed call golden set + synthetic caller simulator; slot accuracy + latency gates in CI.
7. **L5: 300 → 3,000 concurrent?** — Media servers autoscale on active calls; STT/TTS vendor quotas are the real limit → multi-vendor; regional pods.
8. **L5: HIPAA?** — BAA, encryption, redaction, minimum-necessary PHI in prompts, audit logs of tool calls.

## §10 Trade-offs + defeaters
| Decision | Chosen | Alt | Flips |
|---|---|---|---|
| Pipeline | cascade STT/LLM/TTS | E2E speech model | non-transactional use |
| Dialog control | code state machine | model-driven | never for bookings |
| Model | Flash | Pro | never (latency) |
| State | Redis + Postgres | in-process | never |
- Defeaters: "let the LLM manage the whole call" · "batch STT then respond" · "no confirmation, it slows the call".

## §11 MVP ladder
- MVP0: Twilio → streaming STT → ADK agent → TTS, one intent (book), read-back, writes to sandbox scheduler.
- MVP1: state machine for 3 intents, barge-in, Redis live state, transfer.
- MVP2: identity verification, idempotent bookings, Langfuse, 100-call golden replay.
- MVP3: synthetic caller simulator, multi-region, vendor failover, PHI redaction.

## §12 Memorization card
- Pitch: streaming voice cascade around a code-owned booking state machine, with confirm-before-write and warm human transfer.
- Autonomy: L2 + L3 tool step; trigger = dialog open-ended, transaction closed.
- Numbers: p95 1.5 s · 300 concurrent · 30 calls/pod · 3 re-prompts · $0.15/call.
- Failures: laggy turns · wrong-patient write · lost call state.
- Defeaters: LLM runs the call · no read-back · batch STT.
- MVP0→1→2: one-intent streaming call → state machine + barge-in + transfer → verification + idempotency + evals.
- Done when: break down the latency budget · draw per-call process · list transfer triggers.

## References
1. https://github.com/pipecat-ai/pipecat
2. https://github.com/livekit/agents
3. https://ai.google.dev/gemini-api/docs/live
4. https://google.github.io/adk-docs/streaming/
