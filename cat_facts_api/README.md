# Cat Facts REST API App

Small Python module for the Cat Facts API at `https://catfact.ninja`.

It keeps the external API shape isolated behind an adapter and normalizes every fact into:

```python
SourceRecord(source, id, text, raw)
```

That gives the app a clean JSON round trip:

```text
Cat Facts JSON -> Python dict -> SourceRecord -> JSON
```

## Run the Local API

```bash
/Users/Shared/apps/miniforge3/envs/lpy/bin/python -m cat_facts_api serve --host 127.0.0.1 --port 8000
```

## Endpoints

`GET /fact`

Returns one normalized random cat fact.

```json
{
  "source": "catfacts",
  "id": "random:...",
  "text": "Cats ...",
  "raw": {
    "fact": "Cats ...",
    "length": 42
  }
}
```

`GET /facts?limit=5&page=1`

Returns normalized paginated facts plus upstream pagination metadata.

`GET /facts?limit=20&page=1&q=sleep`

Fetches one page from Cat Facts and filters that page locally by fact text.

## CLI Examples

```bash
/Users/Shared/apps/miniforge3/envs/lpy/bin/python -m cat_facts_api fact
/Users/Shared/apps/miniforge3/envs/lpy/bin/python -m cat_facts_api facts --limit 5 --page 1
/Users/Shared/apps/miniforge3/envs/lpy/bin/python -m cat_facts_api facts --limit 20 --page 1 --query sleep
```
