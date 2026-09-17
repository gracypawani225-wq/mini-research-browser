"""A polished, source-first terminal interface for mini-research-browser."""

from __future__ import annotations

import os
from typing import Annotated

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from .agents import EvidenceAgent, SearchAgent, Source, WriterAgent


app = typer.Typer(
    name="research",
    help="Search the web, inspect evidence, and write cited answers.",
    no_args_is_help=True,
    add_completion=False,
)
console = Console()


def _sources_table(sources: list[Source]) -> Table:
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("#", style="bold", width=4)
    table.add_column("Source", ratio=1)
    table.add_column("Relevance", justify="right", style="green", width=10)
    for index, source in enumerate(sources, start=1):
        table.add_row(
            str(index),
            f"[link={source.url}]{source.title}[/link]\n[dim]{source.domain} · {source.snippet}[/]",
            str(source.score),
        )
    return table


def _research(query: str, limit: int) -> list[Source]:
    with console.status("Search agent is finding sources…", spinner="dots"):
        found = SearchAgent().search(query, limit=max(limit * 2, 8))
    return EvidenceAgent().select(query, found, limit=limit)


@app.command()
def search(
    query: Annotated[str, typer.Argument(help="Topic or question to research.")],
    limit: Annotated[int, typer.Option("--limit", "-n", min=1, max=10, help="Number of sources to show.")] = 5,
) -> None:
    """Find and rank useful web sources, with no AI key required."""
    try:
        evidence = _research(query, limit)
    except RuntimeError as error:
        console.print(f"[red]{error}[/]")
        raise typer.Exit(1)
    if not evidence:
        console.print("[dim]No useful sources found. Try a more specific query.[/]")
        return
    console.print(f"[bold]Evidence agent selected {len(evidence)} sources[/]\n")
    console.print(_sources_table(evidence))


@app.command()
def ask(
    question: Annotated[str, typer.Argument(help="A question to answer from web evidence.")],
    limit: Annotated[int, typer.Option("--limit", "-n", min=1, max=10, help="Number of sources to use.")] = 5,
) -> None:
    """Search, rank evidence, then ask Gemini for a cited answer."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        console.print("[yellow]GEMINI_API_KEY is not set. `research search` still works without it.[/]")
        raise typer.Exit(1)
    try:
        evidence = _research(question, limit)
        with console.status("Writer agent is drafting from the selected evidence…", spinner="dots"):
            answer = WriterAgent().answer(question, evidence, api_key)
    except RuntimeError as error:
        console.print(f"[red]{error}[/]")
        raise typer.Exit(1)
    console.print(Panel(Markdown(answer), title="Research answer", border_style="cyan"))
    if evidence:
        console.print("\n[bold]Sources used[/]")
        console.print(_sources_table(evidence))


if __name__ == "__main__":
    app()
