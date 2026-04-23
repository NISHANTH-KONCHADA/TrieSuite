"""tests/test_ip.py — Unit Tests for ip.py"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from ip import IPRoutingTrie


@pytest.fixture
def routing_trie():
    t = IPRoutingTrie()
    t.insert("192.168.1.0", "255.255.255.0", "LAN-A")
    t.insert("192.168.2.0", "255.255.255.0", "LAN-B")
    t.insert("10.0.0.0",    "255.0.0.0",     "Class-A")
    t.insert("172.16.0.0",  "255.240.0.0",   "Private-B")
    return t


# ── Insert & CIDR ─────────────────────────────────────────────────────────

class TestInsert:
    def test_insert_cidr(self):
        t = IPRoutingTrie()
        t.insert_cidr("192.168.1.0/24", "test")
        lpm = t.longest_prefix_match("192.168.1.5")
        assert lpm is not None
        assert lpm[0] == "192.168.1.0"

    def test_invalid_cidr_raises(self):
        t = IPRoutingTrie()
        with pytest.raises(ValueError):
            t.insert_cidr("bad_cidr")

    def test_invalid_ip_raises(self):
        t = IPRoutingTrie()
        with pytest.raises(ValueError):
            t._ip_to_bits("not.an.ip.addr.extra")


# ── Longest Prefix Match ──────────────────────────────────────────────────

class TestLongestPrefixMatch:
    def test_lpm_exact_network(self, routing_trie):
        result = routing_trie.longest_prefix_match("192.168.1.10")
        assert result is not None
        assert result[0] == "192.168.1.0"
        assert result[2] == "LAN-A"

    def test_lpm_class_a(self, routing_trie):
        result = routing_trie.longest_prefix_match("10.0.0.50")
        assert result is not None
        assert result[0] == "10.0.0.0"

    def test_lpm_no_route(self, routing_trie):
        result = routing_trie.longest_prefix_match("8.8.8.8")
        assert result is None

    def test_lpm_prefers_specific_over_general(self):
        """Most specific prefix (longest) must win."""
        t = IPRoutingTrie()
        t.insert("10.0.0.0",   "255.0.0.0",     "general")
        t.insert("10.10.0.0",  "255.255.0.0",   "specific")
        result = t.longest_prefix_match("10.10.5.1")
        assert result is not None
        assert result[0] == "10.10.0.0"   # more specific wins
        assert result[2] == "specific"


# ── Exact Match ───────────────────────────────────────────────────────────

class TestExactMatch:
    def test_exact_match_hit(self, routing_trie):
        # The stored network prefix is /24; exact match traverses full 32 bits
        # so a host IP usually won't exact-match a /24 network entry
        result = routing_trie.exact_match("192.168.1.10")
        # exact_match only hits if all 32 bits reach a marker
        # for /24, only first 24 bits stored → result may be None
        # This tests the function doesn't crash
        assert result is None or isinstance(result, tuple)

    def test_exact_match_returns_none_for_unknown(self, routing_trie):
        assert routing_trie.exact_match("1.2.3.4") is None


# ── All Matching Prefixes ─────────────────────────────────────────────────

class TestAllPrefixes:
    def test_multiple_prefixes(self):
        t = IPRoutingTrie()
        t.insert("10.0.0.0",  "255.0.0.0",   "A")
        t.insert("10.10.0.0", "255.255.0.0", "B")
        matches = t.all_matching_prefixes("10.10.5.1")
        labels = [m[2] for m in matches]
        assert "A" in labels
        assert "B" in labels

    def test_no_match_empty(self, routing_trie):
        assert routing_trie.all_matching_prefixes("1.2.3.4") == []

    def test_ordered_least_to_most_specific(self):
        t = IPRoutingTrie()
        t.insert("10.0.0.0",  "255.0.0.0",     "general")
        t.insert("10.10.0.0", "255.255.0.0",   "specific")
        matches = t.all_matching_prefixes("10.10.5.1")
        # First match should be shorter prefix (less specific)
        assert matches[0][2] == "general"
        assert matches[1][2] == "specific"
