from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass
class Result:
    status: str
    summary: str
    next_actions: list[str] = field(default_factory=list)
    artifacts: list[str] = field(default_factory=list)
    details: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)
