from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha1
from typing import Any

import requests

from .models import SourceRecord


class CatFactsError(RuntimeError):
    """Raised when Cat Facts cannot be queried or returns an unexpected shape."""


@dataclass(frozen=True)
class PageResult:
    records: list[SourceRecord]
    pagination: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "records": [record.to_dict() for record in self.records],
            "pagination": self.pagination,
            "count": len(self.records),
        }


class CatFactsClient:
    """Adapter for https://catfact.ninja."""

    DEFAULT_BASE_URL = "https://catfact.ninja"

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 10,
        session: requests.Session | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = session or requests.Session()
        self.headers = {"User-Agent": "cat-facts-api/0.1"}

    def random_fact(self) -> SourceRecord:
        payload = self._get_json("/fact")
        if not isinstance(payload, dict):
            raise CatFactsError("/fact returned a non-object JSON payload")

        fact = str(payload.get("fact", ""))
        record_id = f"random:{sha1(fact.encode('utf-8')).hexdigest()[:12]}"
        return SourceRecord.from_cat_fact(payload, record_id=record_id)

    def facts(self, *, limit: int = 10, page: int = 1) -> PageResult:
        limit = _positive_int(limit, "limit")
        page = _positive_int(page, "page")

        payload = self._get_json("/facts", params={"limit": limit, "page": page})
        if not isinstance(payload, dict):
            raise CatFactsError("/facts returned a non-object JSON payload")

        data = payload.get("data")
        if not isinstance(data, list):
            raise CatFactsError("/facts payload must contain a 'data' list")

        records = [
            SourceRecord.from_cat_fact(item, record_id=f"page:{page}:row:{index}")
            for index, item in enumerate(data)
            if isinstance(item, dict)
        ]

        return PageResult(records=records, pagination=_pagination_from(payload))

    def search_facts(self, query: str, *, limit: int = 10, page: int = 1) -> PageResult:
        normalized_query = query.strip().lower()
        result = self.facts(limit=limit, page=page)

        if not normalized_query:
            return result

        return PageResult(
            records=[
                record
                for record in result.records
                if normalized_query in record.text.lower()
            ],
            pagination={
                **result.pagination,
                "query": query,
                "filter": "local-page-text-match",
            },
        )

    def _get_json(
        self,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> Any:
        url = f"{self.base_url}{path}"

        try:
            response = self.session.get(
                url,
                params=params,
                timeout=self.timeout,
                headers=self.headers,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise CatFactsError(f"Cat Facts request failed: {exc}") from exc

        try:
            return response.json()
        except ValueError as exc:
            raise CatFactsError("Cat Facts returned invalid JSON") from exc


def process_record(record: SourceRecord) -> dict[str, Any]:
    words = record.text.split()
    return {
        "source": record.source,
        "id": record.id,
        "text": record.text,
        "word_count": len(words),
        "preview": record.text[:120],
    }


def _positive_int(value: int, name: str) -> int:
    if not isinstance(value, int) or value < 1:
        raise ValueError(f"{name} must be a positive integer")
    return value


def _pagination_from(payload: dict[str, Any]) -> dict[str, Any]:
    fields = (
        "current_page",
        "first_page_url",
        "from",
        "last_page",
        "last_page_url",
        "next_page_url",
        "path",
        "per_page",
        "prev_page_url",
        "to",
        "total",
    )
    return {field: payload.get(field) for field in fields if field in payload}
