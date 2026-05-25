# Justin Yang — mentor brief: Energy Receipt + Compute Covenant

**For:** Justin Yang (TELUS, Creator Jam mentor), May 25–26, 2026
**About:** Two small specs in the Creator Jam preflight kit —
`specs/preflights/energy-receipt/` and `specs/preflights/compute-covenant/`.
**Posture:** Energy-as-ceremony, not energy-as-commodity. These specs produce
receipts, not offsets.

## Why this spec exists

Two threads converged into the Energy Receipt + Compute Covenant pair:

1. **March 2026 "Computing as Ceremony" framework** established the Intention
   Protocol (every compute call has an intention) and an Impact Accounting
   ledger (every call leaves a receipt). The receipt is reflective discipline,
   not a carbon-accounting product.

2. **May 22 mentor orientation** confirmed that the participant gateway will
   carry the framing *"TELUS Rimouski runs on ~99% renewable Quebec hydro;
   compute as ceremony, code as ceremony."* That framing only holds up if
   teams actually see what their compute consumed.

The Energy Receipt is the per-team artifact a single team produces over the
course of the jam. The Compute Covenant is the jam-level rollup across teams,
with a disclosure-opt-out lane for teams that don't want their numbers public.

**Carol Anne's framing carries through both:** *"What you people call your
natural resources our people call our relatives."* The reflection prompts on
the per-team receipt — *Did the work justify its footprint? What would you do
differently? What reciprocity is owed?* — sit downstream of that. They are not
guilt prompts. They are the teaching that compute is a relationship, not a
commodity.

## What Justin can mentor on

- **TELUS metrics API plumbing.** The Energy Receipt takes `estimated_kwh` per
  event as an input — it does not compute kWh itself. Teams need a working
  path from a TELUS chat call → metrics endpoint → an `estimated_kwh` value
  per event_id. Justin owns this end of the pipe.
- **kWh estimate calibration.** Per the prior context, the metrics API is
  LIVE on Qwen and being extended. For models not yet covered, teams will
  need a fallback (operator-supplied scalar? token-based proxy?). Justin can
  guide a team through what "good enough for a receipt" looks like vs. what
  would be misleading.
- **Energy-as-ceremony framing.** The receipt is deliberately not a
  carbon-offset commodity tool. The BOUNDARY footer is load-bearing. Justin
  can help teams who slip into "we offset X kWh" language pull back to "we
  consumed X kWh, on hydro, and here is our reflection."
- **Composition with Compute Covenant.** A team can produce an Energy Receipt
  for itself. A facilitator (likely Justin or Eve) produces the Compute
  Covenant by collecting the per-team summaries — including from teams that
  opt out of disclosure, who appear in the ecosystem total but not by name.
- **Sovereignty boundaries.** TELUS Rimouski is the sovereign-stack default.
  If a team's compute went through a non-sovereign endpoint (e.g. Claude/GPT
  in `/graph/dev`), that should be visible in the `model` field on each
  event. Justin can mentor on whether/how a team chooses to disclose that.

## Open questions for Justin to answer day-of

These are the questions the spec doesn't (and shouldn't) try to answer
on its own. Bring them into the Friday alignment or Monday opening:

1. **When does the TELUS metrics API extend beyond Qwen?** The receipt accepts
   estimates for any `model` value, but until the API covers gpt-oss and
   Gemma, teams using those models need a documented fallback. Per-model
   target dates would unblock the covenant rollup for the full model catalog.

2. **Can we get water-impact estimates alongside kWh?** Hydro grids have a
   water footprint distinct from carbon. If TELUS surfaces water use per
   compute hour, the receipt could carry a `water_l` field in v0.2 without
   re-architecting. Out of scope for today; surfacing for the conversation.

3. **Per-team vs. per-event granularity — what's stable in the API today?**
   The Energy Receipt assumes per-event `estimated_kwh`. If the metrics
   endpoint only returns per-team or per-session totals, the spec would need
   to be reframed (or events grouped before this tool runs).

4. **What's the embodied carbon per H200 GPU hour?** The Quebec hydro
   operational figure (~1.2 g CO2e/kWh) is the easy citation. Embodied carbon
   from GPU manufacture is the harder, less-cited number. Does TELUS have a
   per-GPU-hour amortized embodied-carbon figure? If yes, it could appear in
   v0.2 as a fixed reference line in the Compute Covenant (not in the
   per-team receipt — embodied is shared infrastructure, not per-team work).

5. **Does TELUS care about Scope 1/2/3 alignment on these receipts?** If
   internal TELUS reporting expects GHG Protocol formatting, the spec's
   receipt-not-offset posture might create friction. Better to surface that
   now than after the jam.

## Boundaries

- Salish-Sea-ecological framings only in sample data and reflection prompts
  (kelp, herring, eelgrass, etc.). No Indigenous-cultural content beyond what
  Carol Anne has explicitly authorized in the worldview JSONs.
- The receipt is not a carbon-offset commodity tool. The BOUNDARY footer must
  remain. Teams may add reflections; teams may not remove the footer.
- Withheld teams in the Compute Covenant: their compute is included in the
  ecosystem total (the electricity ran), their names and per-team numbers are
  not. This is the disclosure default that Justin and a facilitator should
  walk teams through before they commit to public.
- These specs preflight on Gemma + Qwen as a build-attempt exercise. They are
  not certified, blessed, or production-ready. They are receipts of what
  builders produced from a frozen spec — same posture as the rest of the
  preflight kit.
