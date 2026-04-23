# TrieSuite — Real-World Applications of the Trie Data Structure

> A Python project demonstrating how one data structure — the **Trie (prefix tree)** — powers four distinct real-world systems: autocomplete, DNA pattern matching, IP routing, and URL routing.

---

## 📋 Table of Contents
- [Project Overview](#-project-overview)
- [Modules](#-modules)
- [Complexity Analysis](#-complexity-analysis)
- [Installation & Usage](#-installation--usage)
- [Running Tests](#-running-tests)
- [Benchmark Results](#-benchmark-results)
- [Project Structure](#-project-structure)

---

## 🧠 Project Overview

Most CS courses teach Tries as an abstract concept. This project proves their **practical value** by applying the same core data structure to four independent domains:

| Module | Algorithm | Real-World Analogue |
|--------|-----------|---------------------|
| `trie.py` | Trie + Levenshtein | Google/Spotlight search suggestions |
| `dna.py` | Aho-Corasick | BLAST bioinformatics tool |
| `ip.py` | Binary Trie + LPM | Cisco/Juniper router forwarding tables |
| `url.py` | Segment Trie + Wildcards | Express.js / FastAPI routing |

---

## 📦 Modules

### 1. `trie.py` — Autocomplete Engine

Implements a full Trie with:
- **Autocomplete** — prefix-based word suggestions in O(L + K)
- **Fuzzy Search** — Levenshtein edit-distance tolerance (typo-forgiving)
- **Delete** — clean node pruning with no orphaned nodes
- **BFS + DFS traversal** — two independent tree-walk strategies
- **Interactive CLI** — menu-driven interface

```python
trie = Trie()
trie.add_word("apple")
trie.add_word("apply")

print(trie.auto_complete("app"))         # ['apple', 'apply', ...]
print(trie.fuzzy_search("applo", max_dist=1))  # [('apple', 1), ('apply', 1)]
```

### 2. `dna.py` — DNA Pattern Matching (Aho-Corasick)

Extends Trie with **failure links** to build the Aho-Corasick automaton, enabling simultaneous multi-pattern search in a single O(n) pass.

**Why it matters:** Naive approach is O(n × Σ|patterns|). Aho-Corasick does it in O(n + m) regardless of how many patterns exist.

Also includes bioinformatics utilities:
- **GC Content** — thermal stability of DNA
- **Reverse Complement** — Watson-Crick base pairing
- **Open Reading Frame (ORF) finder** — ATG → stop codon detection

```python
aho = AhoCorasickTrie()
aho.add_pattern("AGCT")
aho.add_pattern("CGT")
aho.build_failure_links()

matches = aho.search("AGCTGCTATCGTAGCTAGTTTGCGT")
# {'AGCT': [0, 13], 'CGT': [10, 22], ...}

print(AhoCorasickTrie.gc_content("AGCTGCTA"))   # 50.0
print(AhoCorasickTrie.reverse_complement("ATCG")) # CGAT
```

### 3. `ip.py` — IP Routing (Binary Trie + Longest Prefix Match)

Converts IPv4 addresses to 32-bit binary and stores them in a binary Trie. Implements **Longest Prefix Match (LPM)** — the exact algorithm used by real routers.

Since IPv4 is always 32 bits, all operations are effectively **O(1)**.

Also supports **CIDR notation** (`192.168.1.0/24`).

```python
trie = IPRoutingTrie()
trie.insert("192.168.1.0", "255.255.255.0", "LAN-A")
trie.insert("10.0.0.0",    "255.0.0.0",     "WAN")
trie.insert_cidr("172.16.0.0/12", "Private-B")

result = trie.longest_prefix_match("192.168.1.55")
# ('192.168.1.0', '255.255.255.0', 'LAN-A')
```

### 4. `url.py` — URL Routing with Wildcards

Splits URLs by `/` and stores segments as Trie nodes. Supports **`:param` wildcard segments** for dynamic route matching — exactly like Express.js or FastAPI.

Priority: **exact segments beat wildcards** (correct routing behaviour).

```python
router = URLRoutingTrie()
router.add_url("/user/:id/posts/:postId", "post_detail")
router.add_url("/user/profile",           "static_profile")

result = router.route("/user/42/posts/99")
# {'handler': 'post_detail', 'params': {'id': '42', 'postId': '99'}}

result = router.route("/user/profile")
# {'handler': 'static_profile', 'params': {}}  ← exact wins
```

---

## 📊 Complexity Analysis

| Operation | Naive (List) | Trie | Speedup |
|-----------|-------------|------|---------|
| Autocomplete (prefix p, n words) | O(n × \|p\|) | O(\|p\| + K) | ~n/K × faster |
| Exact word search | O(n) | O(L) | Linear → Constant |
| DNA multi-pattern (text n, patterns) | O(n × Σ\|Pi\|) | O(n + m) | Proportional to # patterns |
| IP lookup (32-bit IPv4) | O(n) table scan | O(32) = O(1) | Constant time always |
| URL routing (depth D) | O(n × D) | O(D) | Linear in routes |

---

## 🚀 Installation & Usage

### Prerequisites
- Python 3.8+
- `pytest` (for tests only)

### Install
```bash
pip install -r requirements.txt
```

### Run individual modules
```bash
# Autocomplete CLI
python trie.py

# DNA pattern matching demo
python dna.py

# IP routing demo
python ip.py

# URL routing demo
python url.py

# Benchmark: Trie vs. linear search
python benchmark.py
```

---

## ✅ Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific module tests
pytest tests/test_trie.py -v
pytest tests/test_dna.py -v
pytest tests/test_ip.py -v
pytest tests/test_url.py -v
```

### Test Coverage
| File | Tests |
|------|-------|
| `test_trie.py` | Insert, search, autocomplete, delete, traversals, fuzzy search, file loading |
| `test_dna.py` | Pattern insert, search positions, failure links, GC content, reverse complement, ORF |
| `test_ip.py` | LPM correctness, CIDR, prefix specificity, exact match, all-prefix listing |
| `test_url.py` | Exact routing, param extraction, wildcard fallback, delete, prefix listing |

---

## ⚡ Benchmark Results

Run `python benchmark.py` to reproduce. Sample output on a 160-word dictionary:

```
Trie autocomplete          0.0021 ms / query
List (linear scan)         0.0089 ms / query

Trie is ~4x faster than linear scan.

(Advantage scales with dictionary size — at 100k words, Trie wins by ~1000x)
```

---

## 🗂 Project Structure

```
dsa project/
├── trie.py              # Core Trie + Autocomplete + Fuzzy Search
├── dna.py               # Aho-Corasick DNA Pattern Matching
├── ip.py                # Binary Trie IP Routing (LPM)
├── url.py               # Segment Trie URL Routing (wildcards)
├── benchmark.py         # Trie vs. Linear Search performance proof
├── words.txt            # 160-word English dictionary
├── test_cases.txt       # IP routing test data
├── requirements.txt     # Python dependencies
├── dsa project.pptx     # Project presentation
└── tests/
    ├── test_trie.py     # 20 unit tests
    ├── test_dna.py      # 15 unit tests
    ├── test_ip.py       # 14 unit tests
    └── test_url.py      # 16 unit tests
```

---

## 👤 Author

**Nishanth Konchada** — Computer Science Engineering
