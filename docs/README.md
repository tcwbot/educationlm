# Education System Profile Documentation

This document explains how to use `profile.md` as a continuously updated learner model that improves content delivery over time.

## Purpose
`profile.md` is the single source of truth for a student's learning state.

It should be updated after each learning interaction so the LLM can adapt:
- quiz difficulty
- lesson style
- pacing
- feedback format
- revision cadence

## Files
- `docs/profile.template.md`: starter template for a student's profile.
- `docs/tutoring-protocol.md`: operational session protocol for adaptive tutoring.
- `docs/session-summary.template.md`: reusable summary format for each session.
- `docs/mcp-tools.md`: model tool-calling design (YouTube recommender).
- `profile.md` (recommended at repo root): active profile for a student.

## Recommended Workflow (CI/CD style)
1. **Collect data** from the learning session (quiz scores, time-on-task, friction points).
2. **Evaluate learning state** (mastery changes, confidence trends, modality signals).
3. **Update `profile.md`** with new evidence and strategy adjustments.
4. **Generate next lesson plan** using updated profile context.
5. **Deliver content + quiz**, then repeat the cycle.

## Continuous Update Rules
- Update profile after every session.
- Never overwrite historical evidence; append to logs.
- Tie strategy changes to measurable signals (score, completion time, retries).
- Record why major changes were made in the changelog.

## Quiz Design Guidance
Use short, frequent quizzes to infer both knowledge and learner type.

Include mixed question formats:
- MCQ for recall
- short answer for conceptual understanding
- practical tasks for transfer/application

Track:
- score
- time spent
- number of attempts
- error patterns
- confidence (self-reported)

## How the LLM Uses the Profile
Prompt pipeline should include:
1. student goals
2. current mastery map
3. learner type signals
4. adaptation rules
5. latest quiz outcomes

The model should then:
- choose teaching style and complexity
- select examples aligned to interests
- decide review timing
- generate targeted remediation where needed

## Bootstrapping a Student
1. Copy `docs/profile.template.md` to `profile.md`.
2. Fill metadata, snapshot, and baseline assessment.
3. Run an initial diagnostic quiz.
4. Populate mastery map and learner-type signals.
5. Start regular session updates.

## Governance Notes
- Keep personal data minimal.
- Maintain consent status.
- Add human review checkpoints for high-stakes decisions.
