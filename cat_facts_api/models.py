from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class SourceRecord:
    """Normalized API record used by the rest of the app."""

    source: str
    id: str
    text: str
    raw: dict[str, Any]

    @classmethod
    def from_cat_fact(
        cls,
        payload: Mapping[str, Any],
        record_id: str,
        source: str = "catfacts",
    ) -> "SourceRecord":
        fact = payload.get("fact")
        if not isinstance(fact, str) or not fact.strip():
            raise ValueError("Cat Facts payload must contain a non-empty 'fact' string")

        return cls(
            source=source,
            id=record_id,
            text=fact,
            raw=dict(payload),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self, *, indent: int | None = None) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "SourceRecord":
        raw = data.get("raw")
        if not isinstance(raw, dict):
            raise ValueError("SourceRecord data must contain a 'raw' object")

        return cls(
            source=str(data["source"]),
            id=str(data["id"]),
            text=str(data["text"]),
            raw=dict(raw),
        )

    @classmethod
    def from_json(cls, json_string: str) -> "SourceRecord":
        data = json.loads(json_string)
        if not isinstance(data, dict):
            raise ValueError("SourceRecord JSON must decode to an object")
        return cls.from_dict(data)
