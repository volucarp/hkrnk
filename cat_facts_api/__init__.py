"""Cat Facts REST API client and local API app."""

from .client import CatFactsClient, CatFactsError, PageResult, process_record
from .models import SourceRecord

__all__ = [
    "CatFactsClient",
    "CatFactsError",
    "PageResult",
    "SourceRecord",
    "process_record",
]
