"""Meeting extraction tests (MI-2, offline): the extraction step with a fake gateway."""

from __future__ import annotations

from truenorth_engine.meetings import extract_decisions
from truenorth_engine.schemas import ExtractedDecision, MeetingExtraction


class _FakeGateway:
    def __init__(self, result: MeetingExtraction) -> None:
        self.result = result
        self.instructions: list[str] = []

    def structured(self, *, instruction, output_format, **kwargs):
        self.instructions.append(instruction)
        assert output_format is MeetingExtraction
        return self.result


def test_extract_decisions_returns_candidates():
    canned = MeetingExtraction(
        summary="Discussed the 2.4 release and a Globex discount.",
        decisions=[
            ExtractedDecision(
                question="Ship release 2.4 tonight?",
                decision_type="release_go_no_go",
                owner="Dana",
                deadline="tonight",
                dissent="QA lead wanted another day",
            ),
            ExtractedDecision(
                question="Approve a 30% discount for Globex?",
                decision_type="discount_approval",
                owner="Sam",
            ),
        ],
    )
    gateway = _FakeGateway(canned)
    out = extract_decisions(gateway, "We agreed Dana ships 2.4 tonight.", title="Release sync")

    assert out.summary.startswith("Discussed")
    assert [d.decision_type for d in out.decisions] == ["release_go_no_go", "discount_approval"]
    assert out.decisions[0].owner == "Dana"
    # The transcript and title are passed into the model instruction.
    assert "Transcript:" in gateway.instructions[0]
    assert "Release sync" in gateway.instructions[0]


def test_extract_decisions_handles_no_decisions():
    gateway = _FakeGateway(MeetingExtraction(summary="No decisions made.", decisions=[]))
    out = extract_decisions(gateway, "General brainstorming, nothing decided.")
    assert out.decisions == []
