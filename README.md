# GitHub Research Agent — Full-Stack Integration Assignment

## What this repo contains today

The `research_agent/` package is a **complete, working Python AI component**. Given a
natural-language request like *"find a github project for parsing pdf files in python"*,
it will:

1. Extract a search topic from the request.
2. Search public GitHub repositories for that topic.
3. Fetch and clean the README of each candidate repo.
4. Ask a small open-weight LLM (`Qwen/Qwen2.5-1.5B-Instruct`, via `transformers`) to
   write a short relevance summary for each candidate.
5. Return a structured result (`ResearchResult`, with a list of `ProjectResult`s and a
   ready-to-print `.summary` string).

```python
from research_agent import ResearchAgent

agent = ResearchAgent()
result = agent.research("find a github project for parsing pdf files in python")
print(result.summary)
```

Setup:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

**The AI logic itself is out of scope for this assignment and should not need to change.**
You are integrating it, not improving it. (If you find an actual bug in it, fix it and
note the fix in your submission notes — that's fair game.)

---

## The assignment

This repo is a take-home exercise to evaluate your ability to **connect a Python AI
component to a Java backend and a web frontend**. There is currently no backend and no
frontend — you are building both, plus whatever glue is needed to bridge the two
languages.

### Your task

1. **Expose the Python AI logic as a service.**
   `ResearchAgent` is a plain Python class today — nothing outside a Python process can
   call it. You need to decide how the Java backend will invoke it. You are free to
   choose the approach; be ready to justify the tradeoff. Reasonable options include:
   - Wrap `ResearchAgent` in a small HTTP service (e.g. Flask/FastAPI) that the Java
     backend calls over REST.
   - Invoke a Python CLI entry point as a subprocess from Java, passing the query in
     and reading structured (e.g. JSON) output back.
   - Something else, if you have a good reason (gRPC, message queue, etc.) — just don't
     over-engineer it for what is a single request/response operation.

   Whatever you pick, do not change `ResearchAgent`'s internal logic — wrap it, don't
   rewrite it.

2. **Build a Java backend.**
   - Accepts a user's free-text research query (e.g. via a REST endpoint).
   - Calls into the Python service/process from step 1.
   - Returns the structured result (project name, URL, stars, relevance summary) as
     JSON to the frontend.
   - Handle the obvious failure modes: the Python side is slow/unreachable, GitHub
     returns nothing, the query is empty, etc. You don't need to be exhaustive — just
     show you thought about it.
   - Framework choice is up to you (Spring Boot is the natural default). Note your
     choice and why in your submission notes if you pick something else.

3. **Build a good-looking frontend.**
   - A single page is enough: a text input for the query, a submit action, and a
     results list showing each project's name, star count, link, and relevance
     summary.
   - Visual polish is required, not optional: a clean, deliberate layout, readable
     typography, and results presented as a nicely styled list/cards — not a raw JSON
     dump or an unstyled bullet list.
   - Loading and empty/error states should be visibly handled with the same visual
     care as the success state, not just functionally present.
   - Framework choice is up to you (plain HTML/CSS/JS, React, Thymeleaf
     server-rendered, etc.).

### What "done" looks like

The assignment is considered complete when, after a **local run of the full project**
(Python side + Java backend + frontend, following your own setup instructions):

- The app comes up and loads correctly with no manual workarounds.
- Submitting a query returns a response with a **low, acceptable response time** — the
  UI should not feel like it's hanging (e.g. show a loading state immediately, and the
  end-to-end request should complete in a reasonable number of seconds, not minutes).
- The result is rendered as a **well-formatted, visually clean response** — styled
  cards/list with project name, stars, link, and relevance summary — not raw JSON or
  unstyled text.

### Explicitly out of scope

- Improving the AI/model logic itself (prompt tuning, model swap, search ranking, etc.)
- Authentication, user accounts, persistence/database.
- Production concerns like horizontal scaling or rate-limit handling beyond basic error
  handling.

If you have spare time after the core flow works end to end and looks good, feel free
to add something from the above and call it out as a bonus — but the core integration,
performance, and visual polish are what's being evaluated.

### What we're evaluating

- Whether the Java ↔ Python integration is sound and the chosen approach is reasonable
  for the problem (not necessarily "the most sophisticated").
- Backend code quality: structure, error handling, API design.
- **Response time**: the app should feel responsive — a visible loading state plus a
  reasonably fast end-to-end round trip.
- **Visual quality of the frontend**: layout, typography, and how the results are
  presented, in addition to whether it functionally works.
- Whether the frontend correctly reflects backend/service state (loading, error, empty,
  success).
- Clarity of your own README/notes: how to run the whole stack, and why you made the
  integration choice you made.

### Deliverables

- Your Java backend source.
- Your frontend source.
- Any changes needed to run the Python side as a service (a new entry point/wrapper is
  expected; do not modify `research_agent/`'s core logic).
- A short `NOTES.md` (or a section in your own README) covering:
  - How to run the whole stack locally, start to finish.
  - Which integration approach you chose and why.
  - Any tradeoffs, shortcuts, or known issues given the time box.

### Time expectation

This is scoped to be doable in a few focused hours, not days. If you're spending
significantly longer, favor finishing the end-to-end flow over polishing any one layer.
