from dataclasses import dataclass
from typing import Protocol


@dataclass(slots=True)
class AISummary:
    summary: str
    risk_hints: list[str]
    model: str


class AIGateway(Protocol):
    async def summarize_question(
        self,
        *,
        title: str,
        content: str,
        answers: list[str],
        request_id: str | None = None,
    ) -> AISummary: ...
