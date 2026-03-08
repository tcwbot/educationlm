# Tutoring Protocol

This protocol defines how each learning interaction should run.

## Session Loop
1. Review learning progress and current goals.
2. Run a quick knowledge assessment (quiz or practice problem).
3. Update mastery levels (0-100%) for affected topics.
4. Adapt teaching style based on learner performance and profile signals.
5. Provide targeted feedback.
6. End with a structured session summary.
7. Feed outcomes into periodic progress reports.
8. Revisit and adjust goals.

## Required Outputs Per Session
- `assessment`: quiz/problem + score + time spent
- `mastery_updates`: topics with old/new mastery values
- `adaptation_decisions`: what changed in explanation style or pacing
- `feedback`: strengths and improvement points
- `session_summary`: concise end-of-session summary
- `next_steps`: practical tasks for next session

## Session Summary Format
Use this structure consistently:
- `covered_topics`:
- `strengths`:
- `areas_to_improve`:
- `mastery_changes`:
- `recommended_next_steps`:
- `goal_adjustments`:

## Reporting Cadence
- `weekly_report`: summarize trend by subject, mastery deltas, and risk topics.
- `monthly_report`: summarize long-term progress, strategy effectiveness, and goal revisions.

## Update Targets
After each session, update:
- `profile.md`:
  - Quiz & Assessment Log
  - Knowledge Mastery Map
  - Learner Type Signals (if new evidence)
  - Content Delivery Strategy
  - Change Log
