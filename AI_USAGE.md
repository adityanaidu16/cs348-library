# AI Usage

This project was developed with assistance from AI tools. This document discloses which tools were used, which tasks they assisted with, and how I verified or modified the generated output. The same information is discussed in the recorded stage 3 demo.

## AI Tools Used

- **Claude Code**, Anthropic's command-line coding agent, running the **Claude Opus 4.7** model. Used interactively in the terminal alongside my editor (VS Code).

## Tasks AI Assisted With

1. **Scaffolding boilerplate.** Generated the initial Django CRUD views, URL routes, and HTML templates from my three model definitions (`Member`, `Book`, `Loan`).
2. **Index recommendations.** Audited my views and proposed candidate columns to index based on observed query patterns.
3. **Concurrency review.** Reviewed my `transaction.atomic()` blocks and identified a lost-update race condition where the availability check sat outside the atomic block.

## Verification and Modification

For each task above, I verified and modified the AI output as follows:

1. **Scaffolding.** I read every generated view and template before committing. I edited the templates to match the visual design I wanted (navigation, color scheme, table layout in `base.html`), tightened the views to match my preferred patterns, and ran the development server to confirm every CRUD path worked end-to-end before moving on.
2. **Index recommendations.** Claude proposed several candidates, including some I rejected. I evaluated each one by tracing it back to a specific query in `views.py` and asking whether that query was hot enough to justify the write-time cost of the index. I kept the five that mapped to real reports or list views (`book_title_idx`, `member_age_idx`, `loan_due_idx`, `loan_return_idx`, `loan_checkout_idx`) and discarded the rest. I confirmed each index was actually created in the database with `sqlite3 db.sqlite3 ".indexes"` and verified the planner uses one of them via `EXPLAIN QUERY PLAN`.
3. **Concurrency review.** I traced the code path Claude flagged myself before accepting the analysis. The race is real: the check on `views.py:138` reads `total_copies` outside the atomic block, so two concurrent checkouts on Postgres could both pass the check. I made a deliberate decision not to fix it in the SQLite version, because SQLite's writer serialization makes the race impossible, and instead to discuss the issue and the Postgres fix (`select_for_update`) in the demo.

## What Was Mine

The model design, database schema, choice of Django and SQLite, project structure, transaction strategy, isolation-level reasoning, and every final code and design decision were mine. AI accelerated the work and acted as a reviewer, but did not replace my judgment.