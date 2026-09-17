from research.agents import EvidenceAgent, Source


def test_evidence_agent_ranks_directly_relevant_sources_first():
    sources = [
        Source("Cats", "https://example.com/cats", "Cats are popular household pets."),
        Source("SQLite FTS5", "https://example.com/fts", "SQLite FTS5 provides full text search."),
        Source("Databases", "https://example.com/db", "Database indexes make text search faster."),
    ]

    selected = EvidenceAgent().select("How does SQLite full text search work?", sources)

    assert [source.title for source in selected] == ["SQLite FTS5", "Databases", "Cats"]
    assert selected[0].score > selected[1].score > selected[2].score


def test_source_domain_is_cleaned_for_display():
    source = Source("Example", "https://www.example.com/path", "A snippet")

    assert source.domain == "example.com"
