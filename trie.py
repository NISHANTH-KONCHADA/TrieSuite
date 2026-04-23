"""
trie.py — Core Trie Data Structure with Autocomplete Engine
============================================================
| Operation        | Time       | Space  |
|------------------|------------|--------|
| insert           | O(L)       | O(L)   |
| search           | O(L)       | O(1)   |
| delete           | O(L)       | O(1)   |
| autocomplete     | O(L + K)   | O(K)   |
| fuzzy_search     | O(W * L²)  | O(L)   |
L = word length, K = completions returned, W = total words in Trie
"""

from __future__ import annotations
from collections import deque
from typing import Dict, List, Optional, Tuple


class Node:
    """Single node in the Trie."""
    __slots__ = ("content", "marker", "children")

    def __init__(self, content: str = ""):
        self.content: str = content
        self.marker: bool = False
        self.children: Dict[str, "Node"] = {}

    def find_child(self, c: str) -> Optional["Node"]:
        return self.children.get(c)

    def append_child(self, child: "Node") -> None:
        self.children[child.content] = child

    def remove_child(self, c: str) -> None:
        self.children.pop(c, None)


class Trie:
    """
    Trie (prefix tree) optimised for string operations.
    Applications: autocomplete, spell-check, prefix filtering.
    """

    def __init__(self):
        self.root = Node()
        self._size: int = 0

    # ── Core Operations ────────────────────────────────────────────────

    def add_word(self, word: str) -> None:
        """Insert word. Time O(L), Space O(L)."""
        word = word.lower().strip()
        if not word:
            return
        current = self.root
        for char in word:
            if char not in current.children:
                current.children[char] = Node(char)
            current = current.children[char]
        if not current.marker:
            current.marker = True
            self._size += 1

    def search_word(self, word: str) -> bool:
        """Exact-match search. Time O(L)."""
        node = self._traverse_to(word.lower().strip())
        return node is not None and node.marker

    def starts_with(self, prefix: str) -> bool:
        """Return True if any word starts with prefix. Time O(L)."""
        return self._traverse_to(prefix.lower().strip()) is not None

    def delete_word(self, word: str) -> bool:
        """Delete word from Trie. Returns True if found & deleted. Time O(L)."""
        word = word.lower().strip()
        if not self.search_word(word):
            return False  # word doesn't exist
        self._delete(self.root, word, 0)
        self._size -= 1
        return True

    def count_words(self) -> int:
        """Return total number of stored words. Time O(1)."""
        return self._size

    # ── Autocomplete ────────────────────────────────────────────────────

    def auto_complete(self, prefix: str, limit: int = 15) -> List[str]:
        """
        Return up to `limit` words starting with prefix.
        Time O(L + K), Space O(K).
        """
        prefix = prefix.lower().strip()
        node = self._traverse_to(prefix)
        if node is None:
            return []
        results: List[str] = []
        self._collect(node, prefix, results, limit)
        return results

    # ── Fuzzy Search (Levenshtein) ──────────────────────────────────────

    def fuzzy_search(self, word: str, max_dist: int = 1) -> List[Tuple[str, int]]:
        """
        Return all words within Levenshtein edit distance `max_dist`.
        Returns sorted list of (word, distance). Time O(W * L²).
        """
        word = word.lower().strip()
        current_row = list(range(len(word) + 1))
        results: List[Tuple[str, int]] = []
        for char, child in self.root.children.items():
            self._fuzzy_recurse(child, char, word, current_row, results, max_dist)
        results.sort(key=lambda x: x[1])
        return results

    # ── Traversals ──────────────────────────────────────────────────────

    def dfs_traversal(self) -> List[str]:
        """Pre-order DFS — alphabetical order. Time O(N)."""
        words: List[str] = []
        self._dfs(self.root, "", words)
        return words

    def bfs_traversal(self) -> List[str]:
        """BFS — level-by-level. Time O(N)."""
        queue = deque([(self.root, "")])
        words: List[str] = []
        while queue:
            node, path = queue.popleft()
            if node.marker:
                words.append(path)
            for char, child in sorted(node.children.items()):
                queue.append((child, path + char))
        return words

    def print_trie(self) -> None:
        for word in self.dfs_traversal():
            print(word)

    # ── Private Helpers ─────────────────────────────────────────────────

    def _traverse_to(self, s: str) -> Optional[Node]:
        current = self.root
        for char in s:
            current = current.find_child(char)
            if current is None:
                return None
        return current

    def _collect(self, node: Node, prefix: str, res: List[str], limit: int) -> None:
        if len(res) >= limit:
            return
        if node.marker:
            res.append(prefix)
        for char, child in node.children.items():
            if len(res) >= limit:
                return
            self._collect(child, prefix + char, res, limit)

    def _dfs(self, node: Node, path: str, words: List[str]) -> None:
        if node.marker:
            words.append(path)
        for char, child in sorted(node.children.items()):
            self._dfs(child, path + char, words)

    def _delete(self, current: Node, word: str, index: int) -> bool:
        if index == len(word):
            if not current.marker:
                return False
            current.marker = False
            return len(current.children) == 0
        char = word[index]
        child = current.find_child(char)
        if child is None:
            return False
        should_delete = self._delete(child, word, index + 1)
        if should_delete:
            current.remove_child(char)
            return len(current.children) == 0 and not current.marker
        return False

    def _fuzzy_recurse(
        self,
        node: Node,
        char: str,
        word: str,
        prev_row: List[int],
        results: List[Tuple[str, int]],
        max_dist: int,
        current_word: str = "",
    ) -> None:
        n = len(word)
        current_row = [prev_row[0] + 1]
        for col in range(1, n + 1):
            insert_cost = current_row[col - 1] + 1
            delete_cost = prev_row[col] + 1
            replace_cost = prev_row[col - 1] + (0 if word[col - 1] == char else 1)
            current_row.append(min(insert_cost, delete_cost, replace_cost))
        if current_row[n] <= max_dist and node.marker:
            results.append((current_word + char, current_row[n]))
        if min(current_row) <= max_dist:
            for next_char, child in node.children.items():
                self._fuzzy_recurse(
                    child, next_char, word, current_row, results, max_dist, current_word + char
                )


# ── File I/O ────────────────────────────────────────────────────────────

def load_dictionary(trie: Trie, filename: str) -> bool:
    """Load words from a text file into the Trie. Returns True on success."""
    try:
        with open(filename, "r") as f:
            for line in f:
                word = line.strip()
                if word:
                    trie.add_word(word)
        return True
    except FileNotFoundError:
        print(f"[ERROR] File '{filename}' not found.")
        return False


# ── Interactive CLI ─────────────────────────────────────────────────────

def main():
    trie = Trie()
    print("Loading dictionary...")
    if not load_dictionary(trie, "words.txt"):
        return
    print(f"Loaded {trie.count_words()} unique words.\n")

    MENU = (
        "\n--- TrieSuite Autocomplete ---\n"
        "1. Autocomplete (prefix search)\n"
        "2. Fuzzy Search (typo tolerance)\n"
        "3. Add Word\n"
        "4. Delete Word\n"
        "5. Exact Search\n"
        "6. Print All Words (DFS)\n"
        "7. Quit\n"
    )

    while True:
        print(MENU)
        try:
            mode = int(input("Choose an option: ").strip())
        except ValueError:
            print("Invalid input.")
            continue

        if mode == 1:
            prefix = input("Enter prefix: ").strip()
            suggestions = trie.auto_complete(prefix)
            if suggestions:
                print(f"\n{len(suggestions)} suggestion(s) for '{prefix}':")
                for w in suggestions:
                    print(f"  - {w}")
            else:
                print(f"No matches for '{prefix}'.")
                if input("Add this word? (y/n): ").lower() == "y":
                    trie.add_word(prefix)
                    print(f"'{prefix}' added. Total: {trie.count_words()}")

        elif mode == 2:
            word = input("Enter word: ").strip()
            try:
                max_d = int(input("Max edit distance [1]: ").strip() or "1")
            except ValueError:
                max_d = 1
            results = trie.fuzzy_search(word, max_d)
            if results:
                print(f"\nFuzzy matches for '{word}':")
                for w, d in results:
                    print(f"  - {w}  (distance: {d})")
            else:
                print("No fuzzy matches found.")

        elif mode == 3:
            word = input("Enter word to add: ").strip()
            trie.add_word(word)
            print(f"'{word}' added. Total: {trie.count_words()}")

        elif mode == 4:
            word = input("Enter word to delete: ").strip()
            if trie.delete_word(word):
                print(f"'{word}' deleted.")
            else:
                print(f"'{word}' not found.")

        elif mode == 5:
            word = input("Enter word: ").strip()
            found = trie.search_word(word)
            print(f"{'Found' if found else 'Not found'}: '{word}'")

        elif mode == 6:
            words = trie.dfs_traversal()
            print(f"\nAll {len(words)} words (alphabetical):")
            for w in words:
                print(f"  {w}")

        elif mode == 7:
            print("Goodbye!")
            break

        else:
            print("Invalid option.")


if __name__ == "__main__":
    main()
