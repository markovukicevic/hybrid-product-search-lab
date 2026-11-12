"""Dependency-free query partitioning; never split or sample individual judgments."""

import hashlib
import unicodedata
from collections import defaultdict
from typing import Any


def normalize_query(value: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", value).casefold().split())


def partition_judgments(
    rows: list[dict[str, Any]], *, seed: int = 42, validation_fraction: float = 0.2,
    max_queries_per_partition: int | None = None,
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any]]:
    """Input must contain all judgments for the defined English ranking subset.

    Official test is preserved in full. Training text overlaps with test are quarantined.
    Identical normalized texts stay together when deriving validation from training.
    Optional caps select whole query IDs in train/validation only.
    """
    if not 0 < validation_fraction < 1:
        raise ValueError("validation_fraction must be between 0 and 1")
    if max_queries_per_partition is not None and max_queries_per_partition < 1:
        raise ValueError("query cap must be positive")
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    seen_pairs: set[tuple[str, str]] = set()
    for row in rows:
        if row["product_locale"] != "us" or row["small_version"] != 1:
            raise ValueError("Input must be the complete US small_version subset")
        if row["esci_label"] not in {"E", "S", "C", "I"}:
            raise ValueError("Unknown ESCI label")
        if row["split"] not in {"train", "test"}:
            raise ValueError("Unknown official split")
        if any(row[k] is None for k in ("query_id", "query", "product_id")):
            raise ValueError("Null query/product key")
        query_id = str(row["query_id"])
        if not normalize_query(row["query"]):
            raise ValueError("Empty query")
        pair = (query_id, str(row["product_id"]))
        if pair in seen_pairs:
            raise ValueError("Duplicate query-product judgment")
        seen_pairs.add(pair)
        groups[query_id].append(row)
    for candidates in groups.values():
        if len({r["split"] for r in candidates}) != 1:
            raise ValueError("Query ID overlaps official train/test")
        if len({r["query"] for r in candidates}) != 1:
            raise ValueError("Query ID maps to multiple query texts")

    def digest(value: str) -> str:
        return hashlib.sha256(f"{seed}:{value}".encode()).hexdigest()

    test_texts = {
        normalize_query(items[0]["query"])
        for items in groups.values() if items[0]["split"] == "test"
    }
    partition_names = ("train", "validation", "test", "quarantine")
    partitions: dict[str, list[str]] = {name: [] for name in partition_names}
    for query_id, items in groups.items():
        row = items[0]
        query_text = normalize_query(row["query"])
        if row["split"] == "test":
            name = "test"
        elif query_text in test_texts:
            name = "quarantine"
        else:
            fraction = int(digest(query_text), 16) / (1 << 256)
            name = "validation" if fraction < validation_fraction else "train"
        partitions[name].append(query_id)
    output = {}
    manifest: dict[str, Any] = {
        "seed": seed, "validation_fraction": validation_fraction,
        "query_cap": max_queries_per_partition, "normalization": "NFKC/casefold/whitespace",
        "partitions": {},
    }
    for name, query_ids in partitions.items():
        query_ids.sort(key=lambda q: (digest(q), q))
        original_queries = len(query_ids)
        if name in {"train", "validation"} and max_queries_per_partition is not None:
            query_ids = query_ids[:max_queries_per_partition]
        output[name] = [
            dict(row) for q in query_ids
            for row in sorted(groups[q], key=lambda r: str(r["product_id"]))
        ]
        manifest["partitions"][name] = {
            "query_ids": query_ids, "queries_before_cap": original_queries,
            "judgments": len(output[name]),
        }
    return output, manifest
