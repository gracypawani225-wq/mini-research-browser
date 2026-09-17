# mini-research-browser

A small, source-first research assistant for the terminal. It follows a deliberately understandable three-agent pipeline inspired by research tools such as Perplexity:

```text
your question
    ↓
Search agent → finds web sources
    ↓
Evidence agent → ranks the most relevant snippets
    ↓
Writer agent → optional Gemini answer with numbered citations
```

It is not a huge autonomous system. Each agent is a small Python class with one job, making the whole project easy to learn from and extend.

## Features

- Web search with DuckDuckGo
- Transparent, keyword-based evidence ranking
- Clickable source links and snippets
- Optional Gemini synthesis constrained to selected source snippets
- Traceable numbered citations
- Minimal dependencies and pytest tests

## Quick start

Requires Python 3.11 or later.

```bash
git clone https://github.com/gracypawani225-wq/mini-research-browser.git
cd mini-research-browser
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

research search "how does SQLite full text search work?"
```

The `search` command works without an AI key. It uses the search agent to find results and the evidence agent to rank them.

## Ask for a cited answer

To enable the writer agent, install the optional Gemini dependency and set your key:

```bash
pip install -e ".[ai]"
export GEMINI_API_KEY="your_key_here"
research ask "How does SQLite FTS5 work?"
```

The writer receives only the selected source snippets, is told not to invent information, and must cite claims using `[1]`, `[2]`, and so on. The source table underneath the answer makes every citation easy to inspect.

## Commands

| Command | What it does |
| --- | --- |
| `research search "topic"` | Find and rank useful sources. No API key needed. |
| `research ask "question"` | Search, select evidence, and request a cited Gemini answer. |
| `--limit 5` | Set how many selected sources to show or use (1–10). |

## Project structure

```text
research/
  agents.py  # the small Search, Evidence, and Writer agents
  cli.py     # Typer + Rich terminal interface
tests/
```

## Development

```bash
pip install -e ".[dev]"
pytest
```

## License

MIT. See [LICENSE](LICENSE).
