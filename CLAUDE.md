# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TripWeaver is an AI travel planning application built with LangGraph and OpenAI. It uses a three-node pipeline (query parser → researcher → planner) to convert a natural language travel query into a full day-by-day itinerary. The UI is a Streamlit app.

## Setup

This project uses `uv` for dependency management and requires Python 3.12+.

```bash
# Install dependencies
uv sync

# Activate the virtual environment
source .venv/bin/activate
```

A `.env` file is required at the project root with:
```
OPENAI_API_KEY=your_key_here
```

## Running

```bash
# Streamlit UI (primary)
streamlit run app.py

# CLI runner
python main.py
```

## Testing

```bash
python tests.py
```

## Architecture

The `trip_weaver` Python package is the core library:

```
trip_weaver/
├── config/settings.py          — loads .env; exposes OPENAI_API_KEY and MODEL_NAME
├── models/gpt_model.py         — shared ChatOpenAI client (model_client); all nodes import from here
├── prompts/
│   ├── query_parser_prompt.py  — QUERY_PARSER_PROMPT: natural language → structured JSON
│   ├── research_prompt.py      — RESEARCH_PROMPT: raw destination facts (no itinerary language)
│   └── planner_prompt.py       — PLANNER_PROMPT: builds the markdown itinerary
├── graph/
│   ├── state.py                — TripweverState TypedDict (query, parsed_params, research, plan)
│   ├── nodes/
│   │   ├── query_parser.py     — node: parses query → parsed_params dict
│   │   ├── researcher.py       — node: researches destination → research dict
│   │   └── planner.py          — node: generates itinerary → plan string
│   └── graph.py                — compiles StateGraph; exports `workflow`
└── utils/utils.py              — shared helpers (currently empty)
```

**Graph flow:** `START → query_parser → researcher → planner → END`

**State shape:**
```python
class TripweverState(TypedDict):
    query: str           # raw user input
    parsed_params: dict  # structured trip params (destination, days, budget, pace, …)
    research: dict       # attractions, meals, transport, weather, tips
    plan: str            # final markdown itinerary
```

`agents.ipynb` is the original prototyping notebook — kept as a reference but not imported by the package.
