---
framework_version: 1.2.2
---

# Job Evaluation Framework

<!-- SETUP: Skill match areas and career goals are personalized by running /setup -->

## Eligibility Gate — run before scoring

If the candidate is not a citizen or permanent resident of the country they are applying in, run this first. It is a hard filter, not a scoring dimension, and it is separate from work-permit *timing*: timing asks "can they work the required hours yet?", eligibility asks "are they permitted to hold this job at all?". A candidate can pass timing and still be categorically excluded.

Read the posting's eligibility / work rights / "who can apply" section **verbatim** and classify:

| Posting wording | Verdict |
|-----------------|---------|
| Names a **citizenship or permanent-residency requirement** ("must be a citizen of X", "permanent resident", "PR required", "full working rights" where the employer means citizen/PR) | **FAIL — hard stop.** Do not score, do not draft. Quote the exact wording back to the user. |
| Requires a **security clearance** at any level | **FAIL** in most countries, since clearance is normally gated on citizenship. Verify the specific scheme rather than assuming. |
| **Explicitly names** the candidate's permit class, or says "international applicants welcome", "visa holders considered", "we sponsor" | **PASS** — verified acceptance. Worth noting as a positive in the application. |
| **Silent** on citizenship or residency | **PROCEED, but mark unverified.** Check the employer's own careers or international-applicant page before drafting. |

**Two rules that are easy to get wrong:**

1. **Silence is not permission.** Large graduate programs frequently gate eligibility on their own website rather than in the job ad. Highest-risk categories: professional-services firms, government and defence, banking, telecommunications, and anything touching critical infrastructure.
2. **A company-wide "we accept international applicants" statement is not role-level permission.** The common pattern is a general welcome followed by a *named list* of the specific programs or service lines it covers. Confirm the **specific posting or stream** appears on that list before drafting.

**Report an eligibility failure to the user with the quoted source** rather than silently dropping the role. They may know something about their own status that the profile does not record.

If the candidate's permit also constrains *hours* or *start date* (a student visa with a term-time cap, a permit that begins on graduation), record that as a second gate under this section during `/setup`, with the specific dates. Do not merge it with the eligibility question above — they fail for different reasons and need different answers.

A role that fails this gate is not scored and not drafted. Everything below applies only to roles that pass it.

## Language Gate — run before scoring

No dimension or gate anywhere in this framework currently checks a posting's language requirements against what the candidate actually speaks - it is not one of the five Scoring Dimensions below, not a field `/scrape` or `/rank` track, and not something `/apply`'s language detection (Step 1, which already extracts a posting's required language generically) has anywhere to report to. This gate adds that check, structured the same way as the Eligibility Gate above: read the posting, classify against profile data, and treat a hard mismatch as FAIL before scoring.

Read the posting's language requirements as stated for **the role itself** — not the language the ad happens to be written in. A posting written in a language you don't work in, for a role that only needs languages you do work in on the job, passes fine; only an explicit job-condition requirement ("fluent X required," "must communicate with the Y team in Z") triggers this check. For each language the posting requires as a job condition, compare it against your Languages table in CLAUDE.md / `01-candidate-profile.md`:

| Posting requirement vs. your Languages table | Verdict |
|---|---|
| Requires a language **not on your table at all** (e.g. "fluent Polish required," "must communicate with the Warsaw team in Russian," and you list no Polish/Russian row) | **FAIL — hard stop.** Do not score, do not draft. Quote the exact requirement line. |
| Requires a language you **do** list, but the posting's stated bar (as written — "fluent," "native," "C1+," "business-level") reads as plausibly **higher** than your declared level | **FLAG, then proceed.** Not a fail. Score and draft normally, but surface the gap explicitly in your report to the user (quote both the posting's requirement and your declared level) so they can judge it themselves — bars like "fluent" vary a lot by company and geography, and a recruiter may be flexible. Never silently drop the posting and never silently treat it as a clean pass. |
| Requires a language you list, at or below your declared level (or the posting doesn't specify a level at all — just names the language) | **PASS.** No note needed. |

Judge the level comparison the same way you judge everything else in this framework: read both sides as written and reason about it, don't force either into a rigid scale — CEFR letters, LinkedIn-style buckets ("professional working proficiency"), and plain-English words ("conversational," "fluent," "native") all appear in the wild and don't map onto each other precisely. When genuinely unsure whether a stated bar exceeds the candidate's level, prefer FLAG over a silent PASS — the human is meant to be the tiebreaker, not the gate.

**Worked example:** a candidate whose Languages table lists Spanish (Native) and English (B1/B2). A posting requiring "fluent Russian" → **FAIL**, Russian isn't declared at all. A posting requiring "fluent English" → **FLAG**, English is declared but "fluent" plausibly exceeds B1/B2 — score and draft the application, but tell the candidate this posting's bar may be a stretch and let them decide. A posting requiring "conversational English" or unspecified English → **PASS**, B1/B2 clears a "conversational" bar cleanly.

## Scoring Dimensions

## Disambiguation & False-Positive Filters — run before scoring

Reject false keyword matches and out-of-scope roles immediately:
- **"Development"**: Reject software development, IT engineering, or business development; keep only *development economics, international development, Entwicklungsökonomie, Entwicklungszusammenarbeit, M&E*.
- **"Trade"**: Reject retail trade, trade marketing, and store merchandising; keep only *international trade, Außenwirtschaft, trade policy, competition economics*.
- **"Tax"**: Reject routine payroll clerks and bookkeeping (`Lohnbuchhaltung`); keep only *tax economics, tax advisory, fiscal policy, public finance*.
- **"GIS"**: Reject electrical gas-insulated switchgear (*Gasisolierte Schaltanlage*); keep only *Geographic Information Systems / spatial econometrics*.
- **Negative Keywords (Hard Reject)**: Senior, Lead, Principal, Director, Head of, Leitung, Leiter, Teamleiter, Schülerpraktikum, Ausbildung, Frischetheke, Verkauf, Vertrieb, Außendienst, Einzelhandel, Pflege, Gehaltsabrechnung, Lohnbuchhaltung, payroll, trade marketing, Backoffice, Callcenter, Versicherungsvertrieb, Immobilienmakler, Maschinenbau, Medizin.
- **Experience Ceiling**: Reject vacancies requiring clearly excessive experience (>2 years for junior/entry level).

## Scoring Dimensions & Weighting (0–100)

Evaluate each surviving job posting against these five dimensions:

### 1. CV & Technical Skills Match (Max: 35 points)
- **30–35 pts:** Direct proficiency in core quantitative tools (Stata, R, Python with pandas/statsmodels, SQL, Econometric modeling, Causal Inference, Panel Data, Microeconometrics).
- **20–29 pts:** General empirical/quantitative requirements, Excel/VBA, basic regression, or easily transferable econometric methods.
- **10–19 pts:** Partial data analysis match; requires significant tool upskilling.
- **0–9 pts:** Non-empirical or misaligned technical requirements.

### 2. Economics Domain Relevance (Max: 25 points)
- **20–25 pts:** Core Volkswirtschaftslehre (VWL), empirical economic research, public policy analysis, development economics, environmental/energy economics, labor economics, competition/antitrust, or public finance.
- **12–19 pts:** Adjacent policy research, market analysis, economic consulting, or quantitative social science.
- **5–11 pts:** General business/data analyst role with minimal economic theory/methods.
- **0–4 pts:** Irrelevant domain.

### 3. Career-Level Fit (Max: 20 points)
- **18–20 pts:** Ideal target level: Junior Economist, PreDoc, Research Assistant, Wissenschaftlicher Mitarbeiter, Working Student (Werkstudent), Graduate / Trainee, Intern (Praktikum), Entry Level ($\le 2$ years experience).
- **10–17 pts:** General entry-level / mid-level with flexible experience requirements.
- **0–9 pts:** Too senior (>2–3 years mandatory experience) or student internship when seeking full-time.

### 4. Location & Remote Fit (Max: 10 points)
- **10 pts:** Germany (nationwide) or full remote within Germany.
- **7–9 pts:** Designated cross-border commuter zone within 60–90 minutes of the German border (e.g. Enschede, Luxembourg, Liège, Strasbourg, Basel, Salzburg, Kufstein, Bregenz).
- **0 pts / FAIL:** Distant international locations requiring foreign relocation without remote compatibility.

### 5. Recency (Max: 10 points)
- **10 pts:** Posted within the last 3 days.
- **5–8 pts:** Posted within 4–7 days.
- **0–4 pts:** Older posting (>7 days); only reported if overall score $\ge 80$.

## Score Classification & Thresholds

Total Score = Sum of dimensions (0 to 100).

- **80–100 — 🔥 Strong Match**: Direct fit on skills and economics domain. Top priority for `/apply` or immediate action.
- **65–79 — ✨ Possible Match**: Solid match with minor gaps or language flag.
- **50–64 — 🔍 Exploratory**: Borderline or adjacent opportunity.
- **< 50 — ❌ Discard / Do Not Report**: Automatically reject and log `reject_reason`.

## Output Format

Present the evaluation as:

```
## Job Fit Evaluation: [Role] at [Company]

| Dimension | Points | Notes |
|-----------|--------|-------|
| CV & Technical Skills | XX / 35 | [e.g. Stata/R, microeconometrics match] |
| Economics Domain | XX / 25 | [e.g. Development economics / policy analysis] |
| Career-Level Fit | XX / 20 | [e.g. Junior / Research Associate fit] |
| Location & Remote | XX / 10 | [e.g. Germany / Cross-border commuter] |
| Recency | XX / 10 | [e.g. Posted 2 days ago] |

**Total Score: XX / 100** — [Strong Match / Possible Match / Exploratory / Reject]
**Language Requirement:** [English C2 / German B1 note]

### Key Strengths
- [bullet points]

### Gaps / Flags
- [bullet points]

### Recommendation
[Apply / Tailor / Skip]
```

## Pre-Application: Call the Employer (Best Practice)

Before writing the application, consider whether the candidate should call the contact person listed in the posting. **Only call if there are substantive questions** - never call just to "be remembered."

### When to Suggest Calling
- The posting has unclear or ambiguous requirements
- It's unclear which competencies are essential vs. nice-to-have
- The role description is vague about day-to-day tasks
- There's a named contact person who invites questions

### Good Questions to Ask
- "What are the primary challenges in this role?"
- "How is time typically divided across the listed responsibilities?"
- "Which competencies are most critical for success in this position?"
- "What does success look like in the first 6-12 months?"

### Rules for the Call
- Prepare a 30-second "elevator pitch" about your background in case they ask
- The call's purpose is **gathering information**, not delivering a pitch
- Take notes - use what you learn to tailor the application
- Reference the conversation naturally in the cover letter ("After speaking with [name], I was especially drawn to...")
