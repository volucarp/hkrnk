from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qs, urlparse

from .client import CatFactsClient, CatFactsError


class CatFactsHTTPRequestHandler(BaseHTTPRequestHandler):
    client = CatFactsClient()
    server_version = "CatFactsAPI/0.1"

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        query = parse_qs(parsed.query)

        try:
            if path == "/":
                self._send_json(
                    {
                        "service": "cat-facts-api",
                        "endpoints": ["/fact", "/facts", "/health"],
                    }
                )
            elif path == "/health":
                self._send_json({"status": "ok", "service": "cat-facts-api"})
            elif path == "/fact":
                self._send_json(self.client.random_fact().to_dict())
            elif path == "/facts":
                limit = _query_int(query, "limit", default=10)
                page = _query_int(query, "page", default=1)
                search = _query_string(query, "q")

                result = (
                    self.client.search_facts(search, limit=limit, page=page)
                    if search
                    else self.client.facts(limit=limit, page=page)
                )
                self._send_json(result.to_dict())
            else:
                self._send_error(
                    HTTPStatus.NOT_FOUND,
                    "not_found",
                    f"Unknown endpoint: {path}",
                )
        except ValueError as exc:
            self._send_error(HTTPStatus.BAD_REQUEST, "bad_request", str(exc))
        except CatFactsError as exc:
            self._send_error(HTTPStatus.BAD_GATEWAY, "upstream_error", str(exc))

    def _send_json(self, payload: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_error(self, status: HTTPStatus, code: str, message: str) -> None:
        self._send_json(
            {"error": {"code": code, "message": message}},
            status=status,
        )


def make_handler(client: CatFactsClient) -> type[CatFactsHTTPRequestHandler]:
    class ConfiguredCatFactsHTTPRequestHandler(CatFactsHTTPRequestHandler):
        pass

    ConfiguredCatFactsHTTPRequestHandler.client = client
    return ConfiguredCatFactsHTTPRequestHandler


def run(host: str = "127.0.0.1", port: int = 8000, client: CatFactsClient | None = None) -> None:
    handler = make_handler(client or CatFactsClient())
    server = ThreadingHTTPServer((host, port), handler)
    print(f"Cat Facts API listening on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Cat Facts API")
    finally:
        server.server_close()


def _query_int(query: dict[str, list[str]], name: str, *, default: int) -> int:
    values = query.get(name)
    if not values or values[0] == "":
        return default

    try:
        value = int(values[0])
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer") from exc

    if value < 1:
        raise ValueError(f"{name} must be a positive integer")
    return value


def _query_string(query: dict[str, list[str]], name: str) -> str:
    values = query.get(name)
    return values[0] if values else ""
