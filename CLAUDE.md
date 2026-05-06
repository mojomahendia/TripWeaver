# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TripWeaver is a multi-agent AI travel planning application built with LangChain and OpenAI. The system uses specialized agents (planner, researcher) organized into teams (holiday_team) to collaboratively generate trip plans.

## Setup

This project uses `uv` for dependency management and requires Python 3.12+.

```bash
# Install dependencies
uv sync

# Activate the virtual environment
source .venv/bin/activate
```

The package is installed in editable mode — run `pip install -e .` if working outside uv.

A `.env` file is required at the project root with:
```
OPENAI_API_KEY=your_key_here
```

## Running

```bash
# Entry point (currently a stub)
python main.py

# Run the app
python app.py
```

## Testing

```bash
python tests.py
```

## Architecture

The `trip_weaver` Python package is the core library, structured as:

- **`config/settings.py`** — loads `.env` and exposes `OPENAI_API_KEY` and `MODEL_NAME` (`gpt-4o-mini`). All modules should import settings from here rather than calling `os.getenv` directly.
- **`models/gpt_model.py`** — instantiates a shared `ChatOpenAI` client (`model_client`) via `langchain-openai` with streaming enabled. Agents should use this shared client.
- **`agents/`** — individual agent definitions. `planner.py` and `researcher.py` are the intended agents; each should encapsulate a LangChain runnable or agent executor.
- **`teams/holiday_team.py`** — orchestrates the planner and researcher agents into a cohesive workflow for holiday trip planning.
- **`utils/utils.py`** — shared helper functions for agents and teams.

`template.py` at the root is a one-time scaffolding script (not part of the runtime); it created the directory/file structure and can be ignored.
