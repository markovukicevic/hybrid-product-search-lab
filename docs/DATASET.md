# ESCI data provenance and preparation contract

## Source files

The source repository is [amazon-science/esci-data](https://github.com/amazon-science/esci-data), pinned for this preparation run to commit `7916cdf6ab75a462e77f20ab40428a10923998d5`. The source declares Apache-2.0; its `LICENSE` and `NOTICE` are preserved in local `data/raw/`. Raw and prepared data are ignored by Git and are not committed.

The files were downloaded from the pinned commit and verified with SHA-256:

| File | Bytes | Source rows | SHA-256 |
| --- | ---: | ---: | --- |
| `shopping_queries_dataset_examples.parquet` | 51,286,808 | 2,621,288 | `4a735b693b4a424a6fc67f5be6e4c811495c488bbf66d02a602d308b2744263a` |
| `shopping_queries_dataset_products.parquet` | 1,108,857,465 | 1,814,924 | `25124442d064d64b26f74082d6fa09438d679efc0c183cf28d19064a2b65a265` |

Physical Parquet inspection used PyArrow. Examples fields are `example_id:int64`, `query:string`, `query_id:int64`, `product_id:string`, `product_locale:string`, `esci_label:string`, `small_version:int64`, `large_version:int64`, and `split:string`; the physical file also contains an upstream pandas index field `__index_level_0__:int64`. Product fields are `product_id`, `product_title`, `product_description`, `product_bullet_point`, `product_brand`, `product_color`, and `product_locale`, all strings. Join on `(product_locale, product_id)`, never product ID alone.

## Measured Task 1 US subset

Filter examples to `product_locale=us` and `small_version=1`. Measured counts match the upstream README: train has 20,888 queries / 419,653 judgments; test has 8,956 queries / 181,701 judgments. The full US catalog from the pinned products file contains 1,215,854 products. These counts are from the downloaded files, not estimates.

The successful reproducible preparation run is under `data/prepared/run-2026-11-12-seed42-cap100-provenance/`. Its manifest records the pinned revision, direct source URLs, SHA-256, byte sizes, physical schemas, row counts, seed, selected query IDs, and output counts. It uses seed 42 and caps train and validation at 100 queries each; the cap never applies to official test or catalog. Output counts: train 100 queries / 2,039 judgments; validation 100 / 1,962; test 8,956 / 181,701; quarantine 0; catalog 1,215,854 products. The query IDs and judgment counts reproduced from the complete source with the same seed and cap. Every selected query retained all candidates, official test was retained in full, and normalized query text was disjoint across train, validation, and test. No training query text overlapped test, so quarantine was empty.

## Splits, sampling, and evaluation

Official test rows remain intact. Reject query IDs spanning official splits. Quarantine training queries whose normalized text matches official test text. Normalize with Unicode NFKC, case folding and whitespace collapse; this does not prove semantic deduplication. Assign normalized training texts to validation with a seeded SHA-256 threshold (20% by default, approximately rather than exactly). Optional caps select whole query IDs deterministically and keep every candidate for those IDs. Quarantine is excluded from training and tuning. Test labels must not tune models.

Full catalog means all US products from the recorded products-file revision, even when query sampling is enabled. Products outside judgments have unknown relevance.

Use linear nDCG@10 gains E=1, S=0.1, C=0.01, I=0. These are direct gains, not relevance levels to exponentiate. Recall@10 relevance is E or S. Report metrics for queries with positive sets and separately report zero-positive query exclusions. For catalog retrieval, report recall of known relevant products and judged fraction at 10; do not interpret unjudged products as confirmed irrelevant. Keep judged-candidate ranking and full-catalog retrieval results separate.

## Reproduce preparation

The lightweight data profile installs locked pandas/PyArrow dependencies without model or evaluator packages. With the raw files in `data/raw/`, run:

```sh
POSTGRES_PASSWORD=local-verification-password docker compose -f compose.yaml -f compose.data.yaml build api
POSTGRES_PASSWORD=local-verification-password docker compose -f compose.yaml -f compose.data.yaml run --rm --no-deps api \
  python -m app.prepare_data --source /data/raw --output /data/prepared/run-001 \
  --source-revision 7916cdf6ab75a462e77f20ab40428a10923998d5 --seed 42 --query-cap 1000
```

Choose a new output directory for each run; existing directories are rejected. A successful run writes train/validation/test/quarantine Parquet, the complete US catalog, and `manifest.json`. A manifest marks completion; interrupted output directories must not be treated as complete. Preparation currently loads source tables into memory; the successful capped run completed on the local Docker Desktop host. PostgreSQL ingestion, migrations, retrieval, and search evaluation are not implemented.
