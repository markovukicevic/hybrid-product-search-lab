import unittest

from app.dataset import partition_judgments


def judgments(query_id, query, split="train"):
    return [dict(query_id=query_id, query=query, split=split, product_locale="us",
                 small_version=1, product_id=f"p{i}", esci_label=label)
            for i, label in enumerate(("E", "S", "C", "I"))]


class PartitionTests(unittest.TestCase):
    def test_preserves_all_candidates_and_official_test(self):
        rows = [r for i in range(50) for r in judgments(i, f"query {i}")]
        rows += judgments(100, "held out", "test") + judgments(101, "other test", "test")
        result, _ = partition_judgments(rows, max_queries_per_partition=2)
        self.assertEqual(len(result["test"]), 8)
        for name in ("train", "validation"):
            self.assertEqual(len(result[name]), 8)
            for query_id in {r["query_id"] for r in result[name]}:
                self.assertEqual(sum(r["query_id"] == query_id for r in result[name]), 4)

    def test_normalized_text_overlap_is_quarantined(self):
        rows = judgments(1, "  Blue SHOE ") + judgments(2, "blue shoe", "test")
        result, _ = partition_judgments(rows)
        self.assertEqual(len(result["quarantine"]), 4)
        self.assertEqual(len(result["test"]), 4)
        self.assertFalse(result["train"] or result["validation"])

    def test_stable_under_input_reordering_and_same_text_grouping(self):
        rows = judgments(1, "A shoe") + judgments(2, "a SHOE")
        first, manifest = partition_judgments(rows)
        second, other = partition_judgments(list(reversed(rows)))
        self.assertEqual(first, second)
        self.assertEqual(manifest, other)
        self.assertEqual(sorted([len(first["train"]), len(first["validation"])]), [0, 8])

    def test_rejects_id_leakage_and_duplicate_judgments(self):
        with self.assertRaises(ValueError):
            partition_judgments(judgments(1, "shoe") + judgments(1, "shoe", "test"))
        rows = judgments(1, "shoe")
        with self.assertRaises(ValueError):
            partition_judgments(rows + [rows[0]])


if __name__ == "__main__":
    unittest.main()
