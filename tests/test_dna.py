"""tests/test_dna.py — Unit Tests for dna.py"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from dna import AhoCorasickTrie


@pytest.fixture
def built_aho():
    aho = AhoCorasickTrie()
    for pattern in ["AGCT", "CGT", "TTG", "GCTA"]:
        aho.add_pattern(pattern)
    aho.build_failure_links()
    return aho


SEQ = "AGCTGCTATCGTAGCTAGTTTGCGT"


# ── Pattern Insertion ─────────────────────────────────────────────────────

class TestInsert:
    def test_valid_pattern(self):
        aho = AhoCorasickTrie()
        aho.add_pattern("ACGT")  # should not raise

    def test_invalid_characters(self):
        aho = AhoCorasickTrie()
        with pytest.raises(ValueError):
            aho.add_pattern("ACGX")

    def test_lowercase_normalized(self):
        aho = AhoCorasickTrie()
        aho.add_pattern("acgt")  # normalized to ACGT
        aho.build_failure_links()
        matches = aho.search("ACGT")
        assert "ACGT" in matches


# ── Search ────────────────────────────────────────────────────────────────

class TestSearch:
    def test_pattern_found(self, built_aho):
        matches = built_aho.search(SEQ)
        assert "AGCT" in matches
        assert "CGT" in matches

    def test_correct_positions(self, built_aho):
        matches = built_aho.search(SEQ)
        for pattern, positions in matches.items():
            for pos in positions:
                assert SEQ[pos:pos + len(pattern)] == pattern

    def test_empty_sequence(self, built_aho):
        assert built_aho.search("") == {}

    def test_no_match(self, built_aho):
        matches = built_aho.search("AAAAAAAAAA")
        assert matches == {} or all(len(v) == 0 for v in matches.values())

    def test_overlapping_patterns(self):
        aho = AhoCorasickTrie()
        aho.add_pattern("AA")
        aho.add_pattern("AAA")
        aho.build_failure_links()
        matches = aho.search("AAAA")
        assert "AA" in matches
        assert len(matches["AA"]) >= 2


# ── Failure Links ─────────────────────────────────────────────────────────

class TestFailureLinks:
    def test_auto_build_on_search(self):
        aho = AhoCorasickTrie()
        aho.add_pattern("CGT")
        # Search without explicit build — should still work
        matches = aho.search(SEQ)
        assert "CGT" in matches

    def test_rebuild_after_new_pattern(self):
        aho = AhoCorasickTrie()
        aho.add_pattern("CGT")
        aho.build_failure_links()
        aho.add_pattern("TTG")
        # _built flag invalidated
        matches = aho.search(SEQ)
        assert "TTG" in matches


# ── Utilities ─────────────────────────────────────────────────────────────

class TestUtilities:
    def test_gc_content_pure_gc(self):
        assert AhoCorasickTrie.gc_content("GGCC") == 100.0

    def test_gc_content_no_gc(self):
        assert AhoCorasickTrie.gc_content("AATT") == 0.0

    def test_gc_content_mixed(self):
        assert AhoCorasickTrie.gc_content("ACGT") == 50.0

    def test_gc_content_empty(self):
        assert AhoCorasickTrie.gc_content("") == 0.0

    def test_reverse_complement(self):
        assert AhoCorasickTrie.reverse_complement("ATCG") == "CGAT"

    def test_reverse_complement_palindrome(self):
        # ATAT -> complement TATA -> reverse ATAT
        assert AhoCorasickTrie.reverse_complement("ATAT") == "ATAT"

    def test_find_orfs_basic(self):
        # ATG...TAA is a minimal ORF
        seq = "ATGAAATAA"
        orfs = AhoCorasickTrie.find_orfs(seq, min_length=2)
        assert any("ATG" in orf for orf in orfs)
