---
doc_id: kit.participant-agent-context.ruddick-cpp-primer
doc_kind: primer
status: v0
date: 2026-05-25
audience: participants + their LLM agents
---

# Ruddick's Commitment-Pool Primitive — Plain-Language Primer

## What is a commitment pool?

A **commitment pool** is a small piece of shared infrastructure for tracking promises and recognition between a group of people or organisations. It is a generalisation of a community currency, a mutual-aid ledger, a participatory guarantee scheme, and a procurement contract — all of which already exist informally in many communities.

Will Ruddick's 2026 paper *Commitment-pool route graphs for finance and mutual aid* gives the formalism a precise backbone. The point of his work is not to invent a new institution. The point is to **name what is already happening** in places like Sarafu (Kenya, ~26,000 users, years in production), in potlatch traditions, in cooperative finance, in Reconciliation Action Plans — and to make the shapes interoperable across those settings without flattening their cultural specificity.

## The commitment tuple

Every commitment in a pool is described by a small bundle of fields:

> `C = (i, j, K, b, q, χ, t, e, r, m)`

In plain language:

- **`i` — issuer.** Who is making the promise or attesting to what was done.
- **`j` — promisee.** Who the commitment is to.
- **`K` — scope.** What kind of thing this commitment is about (e.g., land transfer, procurement, restoration labour, clean-energy equity).
- **`b` — body.** The actual text or content of the commitment.
- **`q` — quantity.** How much (dollars, hectares, headcount, hours, whatever the unit is).
- **`χ` — temporal orientation.** This is the load-bearing field. Two values: **future** (promissory — "I will") or **past** (certification — "this was done and witnessed").
- **`t` — time.** When the commitment was made or the event happened.
- **`e` — evidence.** Who witnessed, what records exist, how we know.
- **`r` — remedy.** What happens if the commitment is broken or unmet.
- **`m` — metadata.** Methodology notes, source provenance, anything else.

The tuple is small on purpose. It does not try to capture meaning, motivation, or cultural significance — it captures the structural shape that makes commitments composable across settings.

## The CVLE × RVLFHG architecture

Around the tuple, Ruddick defines two parallel sets of interfaces:

**CVLE — the operations every pool performs:**
- **C — Curation.** What gets in. Admissibility rules.
- **V — Valuation.** What it is worth in the pool's terms.
- **L — Limitation.** Caps, throttles, privacy boundaries.
- **E — Exchange.** How commitments flow between participants.

**RVLFHG — the implementation interfaces every pool implements:**
- **R — Registry.** Where the commitments live.
- **V — Value index.** How relative worth is computed.
- **L — Limiter.** What enforces the caps.
- **F — Fee policy.** What costs the pool charges (often zero at small scales).
- **H — Vault / Settlement.** Where physical custody and settlement happen.
- **G — Governance.** Who can change the rules.

You do not need to memorise these. The point is that any pool — a community currency, a procurement program, a settlement-trust ledger, a RAP-tracking system — has these interfaces, even if it has not named them. Naming them lets two pools talk to each other.

## How this maps onto the Jam's work

The Ruddick formalism is load-bearing for the Indigenomics work because four of the Jam's most natural source corpora are already commitment-shaped:

- **The April 30 Indigenomics Economic Survey.** Every response is dual: it is an **assertion** about what is, and a **commitment** about what is offered, needed, dreamt of, or promised. The respondent is `i`; the Institute (or a named Nation) is `j`; the 25-theme tag fixes `K`; the dollar / hectare / headcount figure if any is `q`; the consent posture is `r` and `m`. The pool is the Indigenomics Economic Account itself.
- **The 25-theme ontology.** Each theme is a pool namespace with its own admissibility rules. Theme 4 (Procurement) admits offers, needs, matches, and remedies; Theme 11 (Trusts) admits temporal-scoped commitments with specific custody; Theme 1 (Land Transfer) admits parcel-level transfers with named title.
- **The 350+ Indigenous-won legal cases** (Carol Anne, Apr 17 verbal; Book 2 cites 363+). These are **past-oriented certifications** (χ = past). Court is the issuer; the Nation is the promisee; the body is the ruling text; the remedy is the court order.
- **Reconciliation Action Plans (RAPs).** Future-oriented commitments (χ = future) by corporations and governments. Carol Anne's 2025 RAP-evaluator framework becomes the fulfillment-scoring layer that flips a commitment from promissory (future) to certified (past) when the evidence holds.

## What this means for a Jam team

If your team is building something that records, recognises, scores, or matches promises and what-was-done, you are working with commitment-pool primitives — whether you call them that or not. Three quick checks for your spec:

1. **Are you handling χ — temporal orientation — explicitly?** A draft that mixes "I will" and "we did" without distinguishing them produces fuzzy results. A simple `temporal_orientation: future | past` field on every record is enough at v0.

2. **Are you naming the witness?** Every commitment needs an `e` — evidence / who witnessed. Self-attestation is fine at v0; PGS-quorum, peer-review, and oral / memory-based witnessing (ROLA Appendix B) are v1.5+. If your spec emits records with no witness field, the records cannot ever be certified.

3. **Are you naming the remedy?** What happens if a promise breaks? At v0 the answer can be "redress through continued dialogue" or "public acknowledgement" — not automatic enforcement. But the field should exist; an architecture that records promises with no remedy slot is silently making the wrong design call.

The Ruddick paper itself is at SSRN 6606438, 44 pages. You do not need to read it to use the primitive. You do need to know that the shapes you are building have been built before, in many places, and someone has done the work to make the shapes interoperable. Stand on it.
