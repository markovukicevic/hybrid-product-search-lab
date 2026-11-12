"""Prepare local upstream Parquet files; run inside the research Docker image."""

import argparse
import hashlib
import json
from pathlib import Path

from app.dataset import partition_judgments


def checksum(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    import pandas as pd
    import pyarrow.parquet as pq

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source-revision", required=True, help="Upstream Git commit SHA")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--query-cap", type=int)
    args = parser.parse_args()
    if len(args.source_revision) != 40 or any(
        c not in "0123456789abcdef" for c in args.source_revision
    ):
        parser.error("source-revision must be a full lowercase Git SHA")
    if args.output.exists():
        parser.error("output already exists; choose a new run directory")
    paths = {
        name: args.source / f"shopping_queries_dataset_{name}.parquet"
        for name in ("examples", "products")
    }
    metadata = {
        name: {
            "url": (
                "https://media.githubusercontent.com/media/amazon-science/esci-data/"
                f"{args.source_revision}/shopping_queries_dataset/{path.name}"
            ),
            "sha256": checksum(path),
            "size_bytes": path.stat().st_size,
            "rows": pq.ParquetFile(path).metadata.num_rows,
            "schema": str(pq.read_schema(path)),
        }
        for name, path in paths.items()
    }
    examples = pd.read_parquet(paths["examples"])
    products = pd.read_parquet(paths["products"])
    required_examples = {
        "example_id", "query", "query_id", "product_id", "product_locale", "esci_label",
        "small_version", "large_version", "split",
    }
    required_products = {
        "product_id", "product_locale", "product_title", "product_description",
        "product_bullet_point", "product_brand", "product_color",
    }
    if not required_examples <= set(examples) or not required_products <= set(products):
        raise ValueError("Upstream schema differs from expected columns")
    selected = examples.loc[
        (examples["product_locale"] == "us") & (examples["small_version"] == 1)
    ].copy()
    if selected.empty:
        raise ValueError("No English ranking judgments")
    if selected[list(required_examples)].isna().any().any():
        raise ValueError("Null required example field")
    catalog = products.loc[products["product_locale"] == "us"].copy()
    keys = ["product_locale", "product_id"]
    if catalog[keys].isna().any().any() or catalog.duplicated(keys).any():
        raise ValueError("Invalid catalog composite key")
    joined = selected.merge(catalog[keys], on=keys, how="left", validate="many_to_one",
                            indicator=True)
    if (joined["_merge"] != "both").any():
        raise ValueError("Judgments reference missing products")
    partitions, manifest = partition_judgments(
        selected.to_dict("records"), seed=args.seed, max_queries_per_partition=args.query_cap,
    )
    manifest.update({
        "source_url": "https://github.com/amazon-science/esci-data",
        "source_revision": args.source_revision, "source_files": metadata,
        "catalog_definition": "All product_locale=us rows in the source products file",
        "catalog_products": len(catalog),
        "official_ranking_counts": selected.groupby("split").agg(
            queries=("query_id", "nunique"), judgments=("query_id", "size")
        ).to_dict("index"),
    })
    args.output.mkdir(parents=True)
    for name, rows in partitions.items():
        pd.DataFrame(rows, columns=selected.columns).to_parquet(args.output / f"{name}.parquet",
                                                             index=False)
    catalog.to_parquet(args.output / "catalog.parquet", index=False)
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"output": str(args.output), "catalog_products": len(catalog)}))


if __name__ == "__main__":
    main()
