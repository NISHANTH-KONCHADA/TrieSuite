# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
"""
benchmark.py — Trie vs. Linear Search Performance Comparison
=============================================================
Proves empirically why a Trie beats a plain list for autocomplete.

| Structure    | Search/Autocomplete  | Insert     |
|--------------|----------------------|------------|
| List (naive) | O(n * L)             | O(1)       |
| Trie         | O(L + K)             | O(L)       |

n = total words, L = prefix length, K = results returned.
The Trie's advantage grows as n grows.
"""

import time
import random
import string
from trie import Trie, load_dictionary


# ── Helpers ──────────────────────────────────────────────────────────────

def trie_autocomplete(trie: Trie, prefix: str, limit: int = 15):
    return trie.auto_complete(prefix, limit)


def list_autocomplete(word_list: list, prefix: str, limit: int = 15):
    """Naive linear scan — O(n * L) per query."""
    return [w for w in word_list if w.startswith(prefix)][:limit]


def benchmark(label: str, fn, queries: list, repeats: int = 500) -> float:
    """Run fn(q) for each query in queries, repeats times. Return avg ms."""
    start = time.perf_counter()
    for _ in range(repeats):
        for q in queries:
            fn(q)
    elapsed = (time.perf_counter() - start) * 1000  # ms
    avg = elapsed / (repeats * len(queries))
    print(f"  {label:<30} {avg:.4f} ms / query")
    return avg


# ── Main ─────────────────────────────────────────────────────────────────

def main():
    print("=" * 55)
    print("  TrieSuite Benchmark — Trie vs. Linear Search")
    print("=" * 55)

    # Build Trie and list from words.txt
    trie = Trie()
    load_dictionary(trie, "words.txt")
    word_list = trie.dfs_traversal()
    n = len(word_list)
    print(f"\nDictionary size: {n} words\n")

    # Generate random prefix queries (1–3 chars)
    random.seed(42)
    prefixes = [random.choice(word_list)[:random.randint(1, 3)] for _ in range(20)]

    print("--- Autocomplete (prefix search) ---")
    t_trie = benchmark("Trie", lambda p: trie_autocomplete(trie, p), prefixes)
    t_list = benchmark("List (linear scan)", lambda p: list_autocomplete(word_list, p), prefixes)
    speedup = t_list / t_trie if t_trie > 0 else float("inf")
    print(f"\n  Trie is {speedup:.1f}x faster than linear scan\n")

    # Fuzzy search benchmark
    print("--- Fuzzy Search (edit distance <= 1) ---")
    sample_words = random.sample(word_list, min(10, n))
    # Slightly corrupt each word
    def corrupt(w):
        if len(w) < 2:
            return w
        i = random.randint(0, len(w) - 1)
        return w[:i] + random.choice(string.ascii_lowercase) + w[i+1:]
    fuzzy_queries = [corrupt(w) for w in sample_words]
    benchmark("Trie fuzzy (Levenshtein)", lambda q: trie.fuzzy_search(q, 1), fuzzy_queries, repeats=50)

    # Exact search benchmark
    print("\n--- Exact Word Search ---")
    exact_queries = random.sample(word_list, min(20, n))
    benchmark("Trie exact search", lambda q: trie.search_word(q), exact_queries)
    benchmark("List (in operator)", lambda q: q in word_list, exact_queries)

    print("\n--- Insert Benchmark ---")
    new_words = ["triebench" + str(i) for i in range(100)]
    fresh_trie = Trie()
    fresh_list = []
    start = time.perf_counter()
    for w in new_words:
        fresh_trie.add_word(w)
    trie_insert_ms = (time.perf_counter() - start) * 1000
    start = time.perf_counter()
    for w in new_words:
        fresh_list.append(w)
    list_insert_ms = (time.perf_counter() - start) * 1000
    print(f"  Trie insert 100 words : {trie_insert_ms:.4f} ms")
    print(f"  List append 100 words : {list_insert_ms:.4f} ms")

    print("\n" + "=" * 55)
    print("  Summary")
    print("=" * 55)
    print(f"  Trie autocomplete is ~{speedup:.0f}x faster than list scan.")
    print("  Trie advantage grows with dictionary size (O(L) vs O(n*L)).")
    print("  Fuzzy search (Levenshtein) is unique to Trie — no list equiv.")
    print("=" * 55)


if __name__ == "__main__":
    main()
