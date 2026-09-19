# GitHub Research Agent — Full-Stack Integration Assignment

## What this repo contains today

The `research_agent/` package is a **complete, working Python AI component**. Given a
natural-language request like *"find a github project for parsing pdf files in python"*,
it will:

1. Extract a search topic from the request.
2. Search public GitHub repositories for that topic (ranked by GitHub's own best-match
   relevance — sorting by star count instead was tried and rejected, since it surfaces
   popular-but-irrelevant repos ahead of small, actually-relevant ones).
3. Fetch and clean the README of each candidate repo.
4. Ask a small open-weight LLM (`Qwen/Qwen2.5-1.5B-Instruct` by default, via
   `transformers`) to write a short relevance summary for each candidate.
5. Return a structured result (`ResearchResult`, with a list of `ProjectResult`s), which
   can be consumed as Python objects, a human-readable `.summary` string, or — most
   relevant for this assignment — as JSON via `.to_dict()` / `.to_json()`.

```python
from research_agent import ResearchAgent

agent = ResearchAgent()
result = agent.research("find a github project for parsing pdf files in python")
print(result.summary)      # human-readable
print(result.to_json())    # machine-readable, this is what the Java backend should consume
```

A CLI entry point is also provided (`research_agent/cli.py`) so the AI logic can be
invoked as a subprocess without writing any Python-side glue — see
[Example workflow](#example-workflow) below.

### Running the Python side

This is plain Python — you do **not** need IntelliJ IDEA (or any Python plugin/IDE at
all) to run it. All you need is Python 3.10+ installed and a terminal — the built-in
Terminal tab in IntelliJ works fine for this if that's where you're already working, but
so does any regular terminal (Terminal.app, PowerShell, a Java-side "Run" configuration
that shells out, etc.). The Python side and the Java side don't need to share an IDE.

macOS/Linux:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Windows (PowerShell):

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Verify it works before wiring up Java:

```bash
python3 -m research_agent.cli "find a github project for parsing pdf files in python"
```

**Important for the integration step:** once dependencies are installed, they live
*inside* `.venv`, not on your system Python. When the Java backend later shells out to
run the CLI, it must call the interpreter **inside that venv** — not a bare `python3`/
`python` — or it'll hit `ModuleNotFoundError` for `transformers`/`requests`:

- macOS/Linux: `.venv/bin/python3 -m research_agent.cli "<query>"`
- Windows: `.venv\Scripts\python.exe -m research_agent.cli "<query>"`

**The AI logic itself is out of scope for this assignment and should not need to change.**
You are integrating it, not improving it. (If you find an actual bug in it, fix it and
note the fix in your submission notes — that's fair game.)

---

## The JSON contract

This is the schema the Java backend needs to parse. It is produced by
`ResearchResult.to_dict()` / `.to_json()` and printed as-is by the CLI:

```json
{
  "query": "string — the original user request, verbatim",
  "topic": "string — the search topic extracted from the request",
  "projects": [
    {
      "name": "string — project name (from its README title, or full_name as fallback)",
      "url": "string — GitHub repo URL",
      "stars": "integer — GitHub star count",
      "relevance": "string — LLM-generated summary of fit for the topic"
    }
  ]
}
```

Notes for the integration layer:

- `projects` can be an **empty array** (no repo matched, or none had a fetchable
  README) — the frontend must render that as an empty state, not an error.
- On failure, the CLI prints `{"error": "..."}` to stdout and exits with a non-zero
  status instead of the schema above — check the exit code, don't assume `projects`
  is always present.
- Every field is always present and of the stated type when the call succeeds — no
  optional/nullable fields to guard against in the success case.

---

## Example workflow

This is a real, captured run — not a hypothetical — showing the full
request → AI pipeline → JSON response flow the Java backend needs to reproduce.

**Command** (this is exactly what a Java backend would run as a subprocess; a small
model is used here for a fast demo run, the default is `Qwen/Qwen2.5-1.5B-Instruct`
for better summary quality):

```bash
python3 -m research_agent.cli "find a github project for parsing pdf files in python" \
    --top-k 3 --model Qwen/Qwen2.5-0.5B-Instruct
```

**stdout (verbatim, pretty-printed for readability):**

```json
{
  "query": "find a github project for parsing pdf files in python",
  "topic": "parsing pdf files in python",
  "projects": [
    {
      "name": "Alegria-Hackathon-Hiring-Webapp",
      "url": "https://github.com/Aakarsh-verma/Alegria-Hackathon-Hiring-Webapp",
      "stars": 7,
      "relevance": "Alegria-Hackathon-Hiring-Webapp is a hiring manager web app designed to automate the process of shortlisting resumes based on AI algorithms. It leverages Python for parsing PDF files and utilizing libraries like PyResParser and Scikit-learn for classification. The app also utilizes MySQL for database management. This project is suitable for those interested in building a mobile or web-based system for managing job applications and shortlisting candidates efficiently."
    },
    {
      "name": "PDF-parsing",
      "url": "https://github.com/Ochy-Brian/PDF-parsing",
      "stars": 0,
      "relevance": "PDF-parsing is a Python library designed to extract text from PDF files using natural language processing techniques. This makes it an excellent choice for tasks such as summarization, translation, and document analysis in NLP applications."
    }
  ]
}
```

What happened under the hood for this run: the query was reduced to the search topic
`"parsing pdf files in python"`, GitHub's search API returned 3 candidate repos ranked
by relevance, one candidate had no fetchable README and was silently skipped (this is
why the response has 2 projects for a `--top-k 3` request — expected behavior, not a
bug), and the model wrote a grounded, README-based summary for each of the other two.

This is what the Java backend receives on stdout; it should parse it directly and the
frontend should render `projects` as the styled result list described above.

## The assignment

This repo is a take-home exercise to evaluate your ability to **connect a Python AI
component to a Java backend and a web frontend**. There is currently no backend and no
frontend — you are building both, plus whatever glue is needed to bridge the two
languages.

### Your task

1. **Expose the Python AI logic as a service.**
   `ResearchAgent` is a plain Python class — nothing outside a Python process can call
   it directly. A JSON-emitting CLI entry point (`python -m research_agent.cli
   "<query>"`, see [The JSON contract](#the-json-contract) and
   [Example workflow](#example-workflow)) is already provided as one way in, callable
   via subprocess. You are free to use it as-is, or take a different approach if you
   have a good reason — e.g. wrapping `ResearchAgent` in a small HTTP service
   (Flask/FastAPI) that the Java backend calls over REST instead of shelling out. Don't
   over-engineer it for what is a single request/response operation (gRPC, message
   queues, etc. are almost certainly overkill here).

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
