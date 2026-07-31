from __future__ import annotations

import argparse
import json
from typing import Sequence

from .client import CatFactsClient
from .server import run


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Cat Facts REST API app")
    subparsers = parser.add_subparsers(dest="command")

    serve_parser = subparsers.add_parser("serve", help="Run the local REST API server")
    serve_parser.add_argument("--host", default="127.0.0.1")
    serve_parser.add_argument("--port", default=8000, type=int)

    subparsers.add_parser("fact", help="Fetch and print one normalized random fact")

    facts_parser = subparsers.add_parser("facts", help="Fetch and print normalized paginated facts")
    facts_parser.add_argument("--limit", default=10, type=int)
    facts_parser.add_argument("--page", default=1, type=int)
    facts_parser.add_argument("--query", default="")

    args = parser.parse_args(argv)
    command = args.command or "serve"

    if command == "serve":
        run(host=getattr(args, "host", "127.0.0.1"), port=getattr(args, "port", 8000))
        return

    client = CatFactsClient()

    if command == "fact":
        print(client.random_fact().to_json(indent=2))
    elif command == "facts":
        result = (
            client.search_facts(args.query, limit=args.limit, page=args.page)
            if args.query
            else client.facts(limit=args.limit, page=args.page)
        )
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        parser.error(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
