# ✈️ TripWeaver

**A multi-stage AI travel planner powered by LangGraph and GPT-4o-mini**

[![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-1.1%2B-green?logo=chainlink&logoColor=white)](https://github.com/langchain-ai/langgraph)
[![LangChain](https://img.shields.io/badge/LangChain-OpenAI-orange?logo=openai&logoColor=white)](https://github.com/langchain-ai/langchain)
[![Model](https://img.shields.io/badge/Model-GPT--4o--mini-blueviolet?logo=openai)](https://platform.openai.com/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-red?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## What It Does

Type a travel request in plain English — TripWeaver runs it through a three-stage LangGraph pipeline that parses your intent, researches the destination, and returns a complete day-by-day itinerary in seconds.

```
Input:  "5 days in Kyoto, Japan — temples, street food, $120/day budget"

Output: A full markdown itinerary with:
        ✓ Morning / Afternoon / Evening time slots
        ✓ Opening hours respected, neighborhoods grouped
        ✓ Meal recommendations with per-person costs
        ✓ Budget breakdown table
        ✓ Practical tips + planner notes
```

> Add a screenshot of the Streamlit UI here once deployed.

---

## How It Works

TripWeaver uses a **deliberately staged** LangGraph pipeline. Each node has a single responsibility, and the state accumulates through the graph:

```
User Query (natural language)
        │
        ▼
┌───────────────────┐
│   Query Parser    │  ← intent extraction + confidence scoring
└────────┬──────────┘    output: destination, days, budget, pace,
         │                       interests, start_date, clarifications
         ▼
┌───────────────────┐
│    Researcher     │  ← facts-only destination research
└────────┬──────────┘    output: attractions, neighborhoods, transport,
         │                       meals, weather, local tips (pure JSON)
         ▼
┌───────────────────┐
│     Planner       │  ← temporal orchestration + itinerary generation
└───────────────────┘    output: markdown itinerary (day-by-day)
```

| Node | Input | Output | Technique |
|------|-------|--------|-----------|
| **Query Parser** | Raw user query | Structured JSON params | `model_client \| JsonOutputParser()` |
| **Researcher** | Trip params (JSON) | Destination facts (JSON) | `model_client \| JsonOutputParser()` |
| **Planner** | Params + research (JSON) | Markdown itinerary | `model_client.invoke()` → raw text |

### Shared State (`TripweverState`)

```python
class TripweverState(TypedDict):
    query: str           # raw user input
    parsed_params: dict  # extracted trip parameters + confidence scores
    research: dict       # attractions, transport, meals, weather, tips
    plan: str            # final markdown itinerary
```

Each node returns a partial dict that LangGraph merges into state — no mutation, fully traceable.

---

## Key Engineering Decisions

**1. Stage separation prevents hallucinated schedules**
The researcher is explicitly prohibited from using any sequencing language ("Day 1", "start with", "first visit"). It only produces raw facts. Temporal orchestration happens exclusively in the planner stage, where pacing rules are applied programmatically.

**2. `JsonOutputParser` chain for structured stages**
The first two nodes use a `model_client | parser` chain to guarantee structured JSON output. The planner intentionally skips parsing — it generates prose markdown directly, which requires no post-processing.

**3. Typed state contract**
`TripweverState` (TypedDict) makes each node's data contract explicit. Every node is a pure function: given the same state, it returns the same output. This makes each node independently unit-testable.

**4. Constraint-driven prompting**
Each prompt contains a **hard rules** section rather than soft suggestions:
- Researcher: 5 explicit prohibitions on scheduling language
- Planner: exact pacing math (`relaxed = 3/day`, `moderate = 4/day`, `intensive = 5–6/day`) + 20–30 min travel buffer rule
- Query parser: confidence scoring (`"high"` if stated, `"low"` if defaulted) with clarification flags for ambiguous inputs

**5. Real-date injection**
`date.today().isoformat()` is prepended to the query parser's system message at runtime, so relative date expressions like "next week" resolve correctly — the LLM doesn't guess from training data.

---

## Tech Stack

| Category | Technology |
|----------|------------|
| Agent Orchestration | [LangGraph](https://github.com/langchain-ai/langgraph) `StateGraph` |
| LLM | OpenAI GPT-4o-mini via [LangChain](https://github.com/langchain-ai/langchain) |
| Output Parsing | `langchain_core.output_parsers.JsonOutputParser` |
| UI | [Streamlit](https://streamlit.io/) |
| State | Python `TypedDict` |
| Config | `python-dotenv` |
| Package Manager | [uv](https://github.com/astral-sh/uv) |
| Language | Python 3.12+ |

---

## Project Structure

```
TripWeaver/
├── app.py                          # Streamlit UI
├── main.py                         # CLI runner
├── trip_weaver/
│   ├── config/
│   │   └── settings.py             # env loading (OPENAI_API_KEY, MODEL_NAME)
│   ├── models/
│   │   └── gpt_model.py            # shared ChatOpenAI client
│   ├── prompts/
│   │   ├── query_parser_prompt.py  # intent extraction prompt
│   │   ├── research_prompt.py      # constraint-driven research prompt
│   │   └── planner_prompt.py       # itinerary generation prompt
│   └── graph/
│       ├── state.py                # TripweverState TypedDict
│       ├── graph.py                # compiled StateGraph (workflow)
│       └── nodes/
│           ├── query_parser.py     # node: NL → structured params
│           ├── researcher.py       # node: params → destination facts
│           └── planner.py          # node: facts → markdown itinerary
├── agents.ipynb                    # original prototyping notebook
└── pyproject.toml
```

---

## Getting Started

### Prerequisites

- Python 3.12+
- An [OpenAI API key](https://platform.openai.com/api-keys)
- [`uv`](https://github.com/astral-sh/uv) package manager

### Installation

```bash
git clone https://github.com/mojomahendia/TripWeaver.git
cd TripWeaver

# Create .env file
echo "OPENAI_API_KEY=your_key_here" > .env

# Install dependencies
uv sync
```

### Run

```bash
# Streamlit UI
streamlit run app.py

# CLI
python main.py
```

---

## Prompt Engineering

All prompts live in `trip_weaver/prompts/` as module-level constants, separate from node logic.

### Query Parser
Converts freeform text into a validated JSON schema. Uses a **defaults table** (budget: $100/day, pace: moderate, travelers: 1) with a **confidence score** per field (`"high"` if explicitly stated, `"low"` if inferred). Populates `clarification_needed[]` when the default is risky (e.g., destination is a country, not a city).

### Researcher
Returns a structured JSON object with 7 sections: destination meta, attractions, neighborhoods, transport options, meal options, weather, and local tips. The prompt contains **explicit negation rules** — the model is never allowed to use sequencing language, group by day, or write narrative prose. This forces factual grounding and prevents the model from leaking planning logic into the data layer.

### Planner
Receives the full research JSON as context and generates a markdown itinerary following a strict format template. Key constraints: neighborhood-aware grouping, mandatory travel buffers, daily meal slots, and a budget conflict flag section ("Planner Notes") that surfaces any gaps or assumptions.

---

## Future Work

- [ ] **Streaming output** — stream the planner's markdown token-by-token to the UI using `workflow.astream()`
- [ ] **Tool-calling researcher** — replace the LLM researcher with real-time web search (Tavily / SerpAPI) for up-to-date attraction data
- [ ] **Conditional routing** — add a clarification node that asks the user follow-up questions before proceeding if `clarification_needed` is non-empty
- [ ] **Node-level unit tests** — test each node in isolation with mocked state; validate JSON schema compliance of researcher output

---

## Author

Built by **Manoj Kumar** as part of an AI engineering portfolio.  
Connect on [LinkedIn](https://www.linkedin.com/in/manojmahendia/) · [GitHub](https://github.com/mojomahendia)
