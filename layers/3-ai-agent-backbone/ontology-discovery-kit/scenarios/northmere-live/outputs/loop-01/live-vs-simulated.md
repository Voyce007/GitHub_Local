# Live agents vs simulation: Northmere TAXCORE, loop 1

This is the first end-to-end run with **live Claude agents**: the BA, EA, DA and
Engineering agents, then the Ontology Steward and Conformance reviews. Each
followed its definition in `.claude/agents/`. All of them worked only from the 12
input files. They were told not to open the simulated run or the simulator code.
Human approvals are left **pending**, because only the named owners can decide them.

## Headline

**The proposed split held up.** Working independently, the live agents produced
the same result as the simulation:
- the same four domains, with the same owner for all 12 TAXCORE tables
- the same column move (NI_NUMBER to National Insurance)
- the same cross-domain event
- the same 6 dependencies
- the same 16 business services.

**Their evidence was stronger and their judgment better.** The live agents raised
47 B-grade elements, against 17 in the simulation, because they cited more
independent sources. The review agents found real risks that the rule-based
simulation could not see.

| | Simulated | Live |
|---|---|---|
| Proposals (validator rejections) | 215 (0) | 324 (0) |
| Elements | 164 | 199 |
| Grades A · B · C · D · X | 0 · 17 · 142 · 2 · 3 | 0 · 47 · 141 · 8 · 3 |
| Contradictions | 3 | 3, the same three |
| Open questions in the register | 12 | 19, plus 10 proposed by the Steward |
| Gates (phases 1, 2, 3) | provisional ×3 | provisional ×3 |
| Domain split, column moves, events, dependencies, services | 4 / 1 / 1 / 6 / 16 | identical |

## What the live agents found that the simulation missed

The full list is in `agent-notes.md` (115 notes) and `reviews/steward-notes.md`.

1. **A possible double issuer of NI numbers.** Batch job J020 (PRC_ALLOCATE_NINO)
   is still scheduled daily in the 2024 job catalogue. That is two years after
   NumberHub replaced TAXCORE's allocation module.
2. **ChildcarePortal reads the TAXCORE database directly**, over JDBC. Which tables
   it reads is unknown, and this is the biggest risk to carving out Childcare. It
   also calls NumberHub and an undocumented `income-verify-svc`.
3. **The eligibility calculation looks wrong.** PRC_CHECK_ELIGIBILITY sums every
   pay period ever recorded and multiplies by 4 to estimate annual income.
4. **The NI contribution calculation has edge cases.** It excludes a deceased
   person's pay periods from before their death, and it has no floor at zero.
5. **Nothing writes some data.** No job writes `DATE_OF_DEATH` or `TC_EMPLOYER`,
   so their real source is unknown. Employer's ownership rests on vocabulary only.
6. **The 2024 catalogue and the 2020 code disagree about J330.** The catalogue says
   it writes `TC_NI_RECORD`, but the code only closes childcare accounts. The
   National Insurance half of the proposed event therefore rests on one line.
7. **The MI extract has no owner.** MI-01 ("All modules") reads every domain, so it
   needs a home after the split.
8. **Several terms are used but never defined:** Parent, Expected Income, Lower
   Earnings Limit and Class 1 Contribution. These are now questions for the
   business owners.

## Weaknesses in the kit that the live run exposed, now fixed

| Problem seen in the live run | Fix |
|---|---|
| The same code list under two names ("Employment Status Code" and "EmploymentStatus") was counted twice | Taxonomy matching ignores naming suffixes; the Engineering agent is told the naming convention |
| Value lists written in different cases ("Live" and "LIVE") would have shown up as false contradictions | Values are normalised before comparison |
| Undefined terms failed the phase-2 gate with no question raised | A "What does X mean?" question goes to the business owner |
| The agents' most useful observations were buried in their notes | `agent-notes.md` is now published for reviewers |
| The event name "PersonChanged" was too generic (raised by the Steward) | Events are named after the business capability: **LifeEventRecorded** |
| NI Category was assigned to PAYE because PAYE also uses it (raised by both reviewers) | A shared code list goes to the domain named in it, by majority of use |
| Reference-model domain labels overwrote decomposition owners, so Party vanished from the summaries (raised by Conformance) | Stored separately as `reference_domain` |
| A National Insurance rule about death was given to Customer (raised by Conformance) | Rules follow the team whose document states them, before vocabulary |

## Recommendations from the reviews, not yet applied

These need a person to decide:
- **Change the event.** The Steward recommends a typed death event (DeathRecorded),
  with Childcare's account closure as Childcare's own rule. It also recommends
  leaving the National Insurance part out until the J330 conflict is settled.
- **Restate the NI Number move.** The Steward suggests: "NumberHub masters the
  number; Customer holds a reference updated by NationalInsuranceNumberAllocated".
  It should wait until the J020 question is answered.
- **Add the missing dependencies to the target picture:** the ChildcarePortal
  database connection, ChildcarePortal to NumberHub, `income-verify-svc`, and MI
  reading all domains.
- **Add the Steward's 10 proposed questions** (in `reviews/steward-notes.md`) to
  the unknowns register once an owner accepts them.
- **Downgrade weak grades.** Conformance flags REL-13 and REL-15 as generously
  graded, and proposes three changes to `config/` rules.

## Files

| File | What it is |
|---|---|
| `live-proposals/{ba,ea,da,eng}.json` | The live agents' raw findings |
| `agent-notes.md` | Their observations |
| `reviews/steward-notes.md` | The Steward's merge, contradiction and decomposition review |
| `reviews/conformance-briefing.md` | The citation spot-check, gate status and one briefing per approver |
| `decomposition/` | Domain ontologies, service contracts, source-to-target mapping and report |
| `../../work/loop-01/approvals.yaml` | Pending decisions for the named owners (not in git) |
