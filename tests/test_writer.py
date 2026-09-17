from research.agents import WriterAgent


def test_writer_does_not_need_ai_when_there_is_no_evidence():
    assert WriterAgent().answer("What is quantum computing?", [], "unused") == (
        "I could not find enough relevant evidence to answer that question."
    )
