"""
dna.py — Multi-Pattern DNA Sequence Analysis (Aho-Corasick Algorithm)
======================================================================
Implements the Aho-Corasick automaton for simultaneous multi-pattern
matching in a single pass over the text.

| Operation               | Time Complexity      | Space Complexity |
|-------------------------|----------------------|------------------|
| insert P patterns       | O(sum of |Pi|)       | O(sum of |Pi|)   |
| build_failure_links     | O(sum|Pi| * alphabet)| O(sum of |Pi|)   |
| search (text length n)  | O(n + m)             | O(m)             |

m = total number of matches found.
Naive approach: O(n * sum|Pi|) — Aho-Corasick is strictly faster.
"""

from __future__ import annotations
from collections import deque, defaultdict
from typing import Dict, List, Optional


class Node:
    """A node in the Aho-Corasick automaton."""
    __slots__ = ("content", "marker", "children", "failure_link", "output")

    def __init__(self, content: str = ""):
        self.content: str = content
        self.marker: bool = False
        self.children: Dict[str, "Node"] = {}
        self.failure_link: Optional["Node"] = None
        self.output: List[str] = []  # patterns that end at this node

    def find_child(self, c: str) -> Optional["Node"]:
        return self.children.get(c)


class AhoCorasickTrie:
    """
    Aho-Corasick automaton for simultaneous multi-pattern DNA matching.

    Usage:
        aho = AhoCorasickTrie()
        aho.add_pattern("AGCT")
        aho.add_pattern("CGT")
        aho.build_failure_links()
        matches = aho.search("AGCTGCTATCGT")
    """

    VALID_BASES = frozenset("ACGT")

    def __init__(self):
        self.root = Node()
        self._patterns: List[str] = []
        self._built: bool = False

    def add_pattern(self, pattern: str) -> None:
        """
        Insert a DNA pattern. Raises ValueError for non-ACGT characters.
        Time: O(|pattern|).
        """
        pattern = pattern.upper().strip()
        if not pattern:
            return
        invalid = set(pattern) - self.VALID_BASES
        if invalid:
            raise ValueError(
                f"Invalid characters {invalid} in pattern '{pattern}'. Use only A, C, G, T."
            )
        self._patterns.append(pattern)
        current = self.root
        for char in pattern:
            if char not in current.children:
                current.children[char] = Node(char)
            current = current.children[char]
        current.marker = True
        current.output.append(pattern)
        self._built = False  # invalidate existing links

    def build_failure_links(self) -> None:
        """
        BFS-build of suffix (failure) links — the core of Aho-Corasick.
        Time: O(sum|patterns| * alphabet_size).
        """
        queue: deque[Node] = deque()
        for child in self.root.children.values():
            child.failure_link = self.root
            queue.append(child)

        while queue:
            current = queue.popleft()
            for char, child in current.children.items():
                queue.append(child)
                failure = current.failure_link
                while failure is not None and char not in failure.children:
                    failure = failure.failure_link
                child.failure_link = (
                    failure.children[char]
                    if failure and char in failure.children
                    else self.root
                )
                # Avoid self-loop at root
                if child.failure_link is child:
                    child.failure_link = self.root
                # Propagate output from failure links (suffix matches)
                child.output = child.output + child.failure_link.output
        self._built = True

    def search(self, text: str) -> Dict[str, List[int]]:
        """
        Search for all inserted patterns simultaneously in `text`.
        Returns {pattern: [0-indexed start positions]}.
        Time: O(n + m)  — single pass over text.
        """
        if not self._built:
            self.build_failure_links()

        text = text.upper().strip()
        current = self.root
        matches: Dict[str, List[int]] = defaultdict(list)

        for i, char in enumerate(text):
            # Follow failure links until we find a match or reach root
            while current is not None and char not in current.children:
                current = current.failure_link
            if current is None:
                current = self.root
                continue
            current = current.children[char]
            for pattern in current.output:
                start = i - len(pattern) + 1
                matches[pattern].append(start)

        return dict(matches)

    # ── Bioinformatics Utilities ─────────────────────────────────────────

    @staticmethod
    def gc_content(sequence: str) -> float:
        """
        GC content (%) — higher GC → more thermally stable double helix.
        GC pairs have 3 H-bonds vs. AT's 2.
        """
        seq = sequence.upper()
        if not seq:
            return 0.0
        return round(sum(1 for c in seq if c in "GC") / len(seq) * 100, 2)

    @staticmethod
    def reverse_complement(sequence: str) -> str:
        """
        Return the reverse complement strand (standard Watson-Crick pairing).
        A↔T, C↔G, then reverse.
        """
        mapping = str.maketrans("ACGT", "TGCA")
        return sequence.upper().translate(mapping)[::-1]

    @staticmethod
    def find_orfs(sequence: str, min_length: int = 3) -> List[str]:
        """
        Naively find Open Reading Frames starting with ATG and ending at
        TAA, TAG, or TGA.  min_length = minimum codon count.
        """
        seq = sequence.upper()
        stop_codons = {"TAA", "TAG", "TGA"}
        orfs: List[str] = []
        for frame in range(3):
            i = frame
            while i < len(seq) - 2:
                codon = seq[i:i+3]
                if codon == "ATG":
                    j = i + 3
                    while j < len(seq) - 2:
                        c = seq[j:j+3]
                        if c in stop_codons:
                            orf = seq[i:j+3]
                            if len(orf) // 3 >= min_length:
                                orfs.append(orf)
                            i = j
                            break
                        j += 3
                i += 3
        return orfs


def main():
    print("DNA Pattern Matching — Aho-Corasick\n")

    aho = AhoCorasickTrie()
    patterns = ["AGCT", "CGT", "TTG", "GCTA"]
    for p in patterns:
        aho.add_pattern(p)
    aho.build_failure_links()

    sequence = "AGCTGCTATCGTAGCTAGTTTGCGT"
    print(f"Sequence  : {sequence}")
    print(f"GC Content: {aho.gc_content(sequence)}%")
    print(f"Rev-Comp  : {aho.reverse_complement(sequence)}\n")

    matches = aho.search(sequence)
    if matches:
        print("Pattern matches found:")
        for pattern, positions in sorted(matches.items()):
            for pos in positions:
                snippet = sequence[pos: pos + len(pattern)]
                print(f"  '{pattern}' at index {pos} → '{snippet}'")
    else:
        print("No matches found.")

    orfs = aho.find_orfs(sequence)
    if orfs:
        print(f"\nOpen Reading Frames: {orfs}")


if __name__ == "__main__":
    main()
