"""tests/test_trie.py — Unit Tests for trie.py"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from trie import Trie, load_dictionary


@pytest.fixture
def populated_trie():
    t = Trie()
    for word in ["apple", "apply", "application", "bat", "batman", "cat", "dog"]:
        t.add_word(word)
    return t


# ── Insert & Size ─────────────────────────────────────────────────────────

class TestInsert:
    def test_size_increases(self, populated_trie):
        assert populated_trie.count_words() == 7

    def test_duplicate_not_counted(self, populated_trie):
        populated_trie.add_word("apple")
        assert populated_trie.count_words() == 7

    def test_empty_string_ignored(self, populated_trie):
        before = populated_trie.count_words()
        populated_trie.add_word("")
        assert populated_trie.count_words() == before

    def test_case_insensitive(self, populated_trie):
        populated_trie.add_word("APPLE")  # already exists as lowercase
        assert populated_trie.count_words() == 7


# ── Search ────────────────────────────────────────────────────────────────

class TestSearch:
    def test_existing_word(self, populated_trie):
        assert populated_trie.search_word("apple") is True

    def test_nonexistent_word(self, populated_trie):
        assert populated_trie.search_word("zebra") is False

    def test_prefix_only_not_word(self, populated_trie):
        # "app" is a prefix of "apple" but not a word itself
        assert populated_trie.search_word("app") is False

    def test_starts_with_true(self, populated_trie):
        assert populated_trie.starts_with("app") is True

    def test_starts_with_false(self, populated_trie):
        assert populated_trie.starts_with("xyz") is False


# ── Autocomplete ──────────────────────────────────────────────────────────

class TestAutocomplete:
    def test_basic(self, populated_trie):
        results = populated_trie.auto_complete("app")
        assert "apple" in results
        assert "apply" in results
        assert "application" in results

    def test_empty_prefix_returns_all(self, populated_trie):
        results = populated_trie.auto_complete("")
        assert len(results) == 7

    def test_no_match_returns_empty(self, populated_trie):
        assert populated_trie.auto_complete("xyz") == []

    def test_limit_respected(self, populated_trie):
        results = populated_trie.auto_complete("", limit=3)
        assert len(results) == 3

    def test_exact_word_as_prefix(self, populated_trie):
        results = populated_trie.auto_complete("bat")
        assert "bat" in results
        assert "batman" in results


# ── Delete ────────────────────────────────────────────────────────────────

class TestDelete:
    def test_delete_existing(self, populated_trie):
        assert populated_trie.delete_word("apple") is True
        assert populated_trie.search_word("apple") is False

    def test_delete_nonexistent_returns_false(self, populated_trie):
        assert populated_trie.delete_word("xyz") is False

    def test_delete_prefix_word_keeps_longer(self, populated_trie):
        populated_trie.delete_word("bat")
        assert populated_trie.search_word("bat") is False
        assert populated_trie.search_word("batman") is True

    def test_delete_updates_count(self, populated_trie):
        before = populated_trie.count_words()
        populated_trie.delete_word("cat")
        assert populated_trie.count_words() == before - 1


# ── Traversals ────────────────────────────────────────────────────────────

class TestTraversals:
    def test_dfs_alphabetical(self, populated_trie):
        words = populated_trie.dfs_traversal()
        assert words == sorted(words)

    def test_bfs_returns_all(self, populated_trie):
        words = populated_trie.bfs_traversal()
        assert len(words) == 7

    def test_dfs_count(self, populated_trie):
        assert len(populated_trie.dfs_traversal()) == 7


# ── Fuzzy Search ──────────────────────────────────────────────────────────

class TestFuzzySearch:
    def test_exact_match_distance_0(self, populated_trie):
        results = dict(populated_trie.fuzzy_search("apple", max_dist=0))
        assert "apple" in results
        assert results["apple"] == 0

    def test_one_typo(self, populated_trie):
        # "applo" is 1 substitution from "apply" / "apple"
        results = dict(populated_trie.fuzzy_search("applo", max_dist=1))
        assert "apple" in results or "apply" in results

    def test_no_match_strict(self, populated_trie):
        results = populated_trie.fuzzy_search("xyz", max_dist=0)
        assert results == []

    def test_sorted_by_distance(self, populated_trie):
        results = populated_trie.fuzzy_search("apple", max_dist=2)
        distances = [d for _, d in results]
        assert distances == sorted(distances)


# ── File Loading ──────────────────────────────────────────────────────────

class TestFileLoad:
    def test_load_dictionary(self, tmp_path):
        f = tmp_path / "words.txt"
        f.write_text("hello\nworld\nfoo\n")
        t = Trie()
        assert load_dictionary(t, str(f)) is True
        assert t.count_words() == 3

    def test_file_not_found(self):
        t = Trie()
        assert load_dictionary(t, "nonexistent.txt") is False
