# Student Profile

## Metadata
- `student_id`: `student-local-001`
- `created_at`: `2026-03-08`
- `last_updated`: `2026-03-08`
- `profile_version`: `v0.2`
- `owner_system`: `educationlm`

## Student Snapshot
- `name`: `TBD`
- `preferred_pronouns`: `TBD`
- `age_range`: `TBD`
- `grade_or_level`: `TBD`
- `goals_short_term`: `Build consistent understanding with weekly quizzes`
- `goals_long_term`: `Reach 80%+ mastery in active subjects`

## Learning Objectives
| Objective ID | Objective | Priority (High/Med/Low) | Target Date | Status |
|---|---|---|---|---|
| OBJ-001 | Establish baseline in math, science, and reading comprehension | High | 2026-03-31 | In Progress |
| OBJ-002 | Identify dominant learner modality with evidence | High | 2026-03-22 | In Progress |

## Baseline Assessment
- `diagnostic_date`: `2026-03-08`
- `current_subjects`: `Math fundamentals, science reasoning, reading comprehension`
- `baseline_strengths`: `Unknown (awaiting first quiz)`
- `baseline_gaps`: `Unknown (awaiting first quiz)`
- `confidence_level_self_reported` (1-5): `Not yet collected`

## Learner Type Signals
> Track observed behaviors and infer learning preferences over time.

### Modality Preferences (confidence-weighted)
- `visual`: `0.17 (low confidence)`
- `auditory`: `0.17 (low confidence)`
- `reading_writing`: `0.17 (low confidence)`
- `kinesthetic`: `0.17 (low confidence)`
- `social`: `0.16 (low confidence)`
- `independent`: `0.16 (low confidence)`

### Cognitive/Behavioral Patterns
- `attention_span_notes`: `Unknown; gather via quiz completion time and follow-up questions`
- `pace_preference` (slow/medium/fast): `Unknown`
- `scaffolding_need` (low/medium/high): `Unknown`
- `feedback_preference` (direct/gentle/mixed): `Unknown`
- `motivation_triggers`: `Unknown`
- `friction_points`: `Unknown`

## Quiz & Assessment Log
| Date | Quiz ID | Topic | Format | Score | Time Spent | Attempt # | Notes |
|---|---|---|---|---:|---|---:|---|
| 2026-03-08 | Q-INIT-001 | Baseline multi-subject diagnostic | MCQ/Short | Pending | Pending | 1 | Created initial quiz set; waiting for answers |

## Knowledge Mastery Map
| Topic | Mastery (0-100) | Evidence | Last Checked | Next Action |
|---|---:|---|---|---|
| Arithmetic foundations | 0 | Pending diagnostic | 2026-03-08 | Complete Q-INIT-001 |
| Science reasoning | 0 | Pending diagnostic | 2026-03-08 | Complete Q-INIT-001 |
| Reading comprehension | 0 | Pending diagnostic | 2026-03-08 | Complete Q-INIT-001 |

## Content Delivery Strategy
- `recommended_lesson_style`: `Adaptive mixed mode until learner type signal confidence > 0.55`
- `recommended_difficulty_band`: `Baseline: easy -> medium`
- `session_structure` (example: 10m explain, 10m guided, 5m quiz): `8m explain, 10m guided, 7m quiz, 5m recap`
- `examples_context` (sports/gaming/business/etc): `Unknown; collect preference next session`
- `review_cadence` (daily/weekly/custom): `Daily micro-quiz + weekly progress summary`
- `intervention_triggers` (e.g., score < 70% twice): `If score < 70% in 2 sessions, reduce pace and increase guided examples`

## Adaptation Rules (LLM Personalization)
- If quiz accuracy drops for 2 consecutive sessions, then: `switch to simpler examples and add one worked example before each question type.`
- If time-to-completion improves while score remains stable, then: `increase difficulty by one level.`
- If confidence is low but mastery is high, then: `add confidence-building reflection and spaced retrieval drills.`
- If learner disengagement signals appear, then: `shorten session blocks and increase interactivity.`

## Session Update Checklist
- [x] Update `last_updated`
- [x] Append latest quiz results
- [x] Recalculate topic mastery
- [x] Update learner type signals
- [x] Adjust delivery strategy
- [x] Record rationale for major profile changes

## Current Quiz Packet
### `Q-INIT-001` (Baseline Diagnostic)
1. Math (MCQ): What is 3/4 + 1/8?
A) 7/8  B) 1  C) 5/8  D) 3/8
2. Math (Short): Solve for x: `2x + 5 = 17`.
3. Science (MCQ): Which process do plants use to convert light into chemical energy?
A) Respiration  B) Photosynthesis  C) Fermentation  D) Digestion
4. Science (Short): Why does increasing surface area usually speed up a chemical reaction?
5. Reading (MCQ): Main idea question pattern: if a paragraph lists causes of ocean pollution, the main idea is usually:
A) Ocean animals are interesting
B) Causes and impacts of ocean pollution
C) How to build boats
D) Why weather changes daily
6. Reading (Short): In 2-3 lines, explain how you find the main idea of a paragraph.
7. Learner signal (Reflection): Which helps you learn best right now?
A) Diagrams/visuals  B) Verbal explanations  C) Reading/writing notes  D) Practice problems
8. Learner signal (Reflection): Do you prefer:
A) Fast challenge  B) Moderate pace with examples  C) Slow step-by-step

## Change Log
| Date | Changed By | Section | Change Summary | Why |
|---|---|---|---|---|
| 2026-03-08 | system/tutor | Full profile initialization | Converted blank template to active baseline profile + first quiz packet | Start continuous assessment and personalization loop |

## Data Quality & Safety
- `data_completeness` (%): `58`
- `last_reviewed_by_human`: `2026-03-08`
- `sensitive_data_present` (yes/no): `no`
- `consent_status`: `pending explicit confirmation`
- `notes`: `Update mastery and learner type immediately after Q-INIT-001 answers are submitted.`
