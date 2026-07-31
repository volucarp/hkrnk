from __future__ import annotations

from typing import Any

import pytest

from cat_facts_api.client import CatFactsClient, process_record
from cat_facts_api.models import SourceRecord
from cat_facts_api.server import _query_int


class FakeResponse:
    def __init__(self, payload: Any) -> None:
        self.payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> Any:
        return self.payload


class FakeSession:
    def __init__(self, payloads: list[Any]) -> None:
        self.payloads = payloads
        self.calls: list[dict[str, Any]] = []

    def get(
        self,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        timeout: float,
        headers: dict[str, str],
    ) -> FakeResponse:
        self.calls.append(
            {
                "url": url,
                "params": params,
                "timeout": timeout,
                "headers": headers,
            }
        )
        return FakeResponse(self.payloads.pop(0))


def test_source_record_json_round_trip() -> None:
    record = SourceRecord.from_cat_fact(
        {"fact": "Cats can jump about six times their length.", "length": 44},
        record_id="example:1",
    )

    assert SourceRecord.from_json(record.to_json()) == record


def test_random_fact_normalizes_cat_fact_payload() -> None:
    session = FakeSession(
        [{"fact": "Cats sleep for a large part of the day.", "length": 42}]
    )
    client = CatFactsClient(session=session)

    record = client.random_fact()

    assert record.source == "catfacts"
    assert record.id.startswith("random:")
    assert record.text == "Cats sleep for a large part of the day."
    assert record.raw == {"fact": "Cats sleep for a large part of the day.", "length": 42}
    assert session.calls[0]["url"] == "https://catfact.ninja/fact"


def test_paginated_facts_normalize_records_and_pagination() -> None:
    payload = {
        "current_page": 2,
        "data": [
            {"fact": "Cats have five toes on their front paws.", "length": 41},
            {"fact": "Most cats dislike water.", "length": 24},
        ],
        "per_page": 2,
        "total": 12,
    }
    session = FakeSession([payload])
    client = CatFactsClient(session=session)

    result = client.facts(limit=2, page=2)

    assert [record.id for record in result.records] == ["page:2:row:0", "page:2:row:1"]
    assert result.records[0].text == "Cats have five toes on their front paws."
    assert result.pagination == {"current_page": 2, "per_page": 2, "total": 12}
    assert result.to_dict()["count"] == 2
    assert session.calls[0]["params"] == {"limit": 2, "page": 2}


def test_search_facts_filters_current_page_text() -> None:
    payload = {
        "current_page": 1,
        "data": [
            {"fact": "Cats sleep for a large part of the day.", "length": 42},
            {"fact": "Cats can rotate their ears.", "length": 28},
        ],
        "per_page": 2,
        "total": 2,
    }
    client = CatFactsClient(session=FakeSession([payload]))

    result = client.search_facts("sleep", limit=2, page=1)

    assert [record.text for record in result.records] == [
        "Cats sleep for a large part of the day."
    ]
    assert result.pagination["query"] == "sleep"
    assert result.pagination["filter"] == "local-page-text-match"


def test_process_record_adds_text_metrics() -> None:
    record = SourceRecord(
        source="catfacts",
        id="example:1",
        text="Cats sleep often.",
        raw={"fact": "Cats sleep often.", "length": 17},
    )

    assert process_record(record) == {
        "source": "catfacts",
        "id": "example:1",
        "text": "Cats sleep often.",
        "word_count": 3,
        "preview": "Cats sleep often.",
    }


def test_query_int_rejects_invalid_values() -> None:
    with pytest.raises(ValueError, match="limit must be a positive integer"):
        _query_int({"limit": ["0"]}, "limit", default=10)
