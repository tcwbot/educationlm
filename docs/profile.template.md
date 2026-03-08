# Student Profile

## Metadata
- `student_id`:
- `created_at`:
- `last_updated`:
- `profile_version`: `v0.1`
- `owner_system`: `educationlm`

## Student Snapshot
- `name`:
- `preferred_pronouns`:
- `age_range`:
- `grade_or_level`:
- `goals_short_term`:
- `goals_long_term`:

## Learning Objectives
| Objective ID | Objective | Priority (High/Med/Low) | Target Date | Status |
|---|---|---|---|---|
| OBJ-001 |  |  |  | Not Started |

## Baseline Assessment
- `diagnostic_date`:
- `current_subjects`:
- `baseline_strengths`:
- `baseline_gaps`:
- `confidence_level_self_reported` (1-5):

## Learner Type Signals
> Track observed behaviors and infer learning preferences over time.

### Modality Preferences (confidence-weighted)
- `visual`:
- `auditory`:
- `reading_writing`:
- `kinesthetic`:
- `social`:
- `independent`:

### Cognitive/Behavioral Patterns
- `attention_span_notes`:
- `pace_preference` (slow/medium/fast):
- `scaffolding_need` (low/medium/high):
- `feedback_preference` (direct/gentle/mixed):
- `motivation_triggers`:
- `friction_points`:

## Quiz & Assessment Log
| Date | Quiz ID | Topic | Format | Score | Time Spent | Attempt # | Notes |
|---|---|---|---|---:|---|---:|---|
| YYYY-MM-DD | Q-001 |  | MCQ/Short/Practical | 0% | 00:00 | 1 |  |

## Knowledge Mastery Map
| Topic | Mastery (0-100) | Evidence | Last Checked | Next Action |
|---|---:|---|---|---|
|  | 0 | Quiz/Project/Discussion | YYYY-MM-DD |  |

## Content Delivery Strategy
- `recommended_lesson_style`:
- `recommended_difficulty_band`:
- `session_structure` (example: 10m explain, 10m guided, 5m quiz):
- `examples_context` (sports/gaming/business/etc):
- `review_cadence` (daily/weekly/custom):
- `intervention_triggers` (e.g., score < 70% twice):

## Adaptation Rules (LLM Personalization)
- If quiz accuracy drops for 2 consecutive sessions, then:
- If time-to-completion improves while score remains stable, then:
- If confidence is low but mastery is high, then:
- If learner disengagement signals appear, then:

## Session Update Checklist
- [ ] Update `last_updated`
- [ ] Append latest quiz results
- [ ] Recalculate topic mastery
- [ ] Update learner type signals
- [ ] Adjust delivery strategy
- [ ] Record rationale for major profile changes

## Change Log
| Date | Changed By | Section | Change Summary | Why |
|---|---|---|---|---|
| YYYY-MM-DD | system/tutor |  |  |  |

## Data Quality & Safety
- `data_completeness` (%):
- `last_reviewed_by_human`:
- `sensitive_data_present` (yes/no):
- `consent_status`:
- `notes`:
