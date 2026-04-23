"""
url.py — URL Routing via Trie (Segment-based with Wildcard Support)
====================================================================
Splits URLs by '/' and stores each segment as a Trie node.
Supports exact match, prefix listing, and wildcard ':param' segments.

| Operation       | Time         | Space  |
|-----------------|--------------|--------|
| add_url         | O(D)         | O(D)   |
| search_url      | O(D)         | O(1)   |
| match_urls      | O(D + K)     | O(K)   |
| route (wildcard)| O(D)         | O(D)   |

D = URL depth (number of segments), K = matched results.

Wildcard segments start with ':' (e.g. ':id', ':username').
They match any single segment during routing (like Express.js).
"""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple


WILDCARD = ":*"  # Internal token for wildcard segments


class Node:
    """A node in the URL Trie. Represents one URL path segment."""
    __slots__ = ("content", "marker", "children", "handler", "params")

    def __init__(self, content: str = ""):
        self.content: str = content
        self.marker: bool = False
        self.children: Dict[str, "Node"] = {}
        self.handler: Optional[str] = None    # e.g. route name / controller
        self.params: Dict[str, str] = {}      # param name for wildcard nodes

    def find_child(self, c: str) -> Optional["Node"]:
        return self.children.get(c)

    def remove_child(self, c: str) -> None:
        self.children.pop(c, None)


class URLRoutingTrie:
    """
    Segment-based URL Trie with wildcard/parameter support.

    Usage:
        router = URLRoutingTrie()
        router.add_url("https://example.com/user/:id/profile")
        router.add_url("https://example.com/home")
        match = router.route("https://example.com/user/42/profile")
        # match -> {"url": "...:id...", "params": {"id": "42"}}
    """

    def __init__(self):
        self.root = Node()

    def _split(self, url: str) -> List[str]:
        """Split URL into segments, filtering empty strings."""
        return [seg for seg in url.split("/") if seg]

    def _is_param(self, segment: str) -> bool:
        """Return True if segment is a route parameter (starts with ':')."""
        return segment.startswith(":")

    def add_url(self, url: str, handler: str = "") -> None:
        """
        Insert a URL (with optional ':param' wildcards) into the Trie.
        Time: O(D).
        """
        url = url.strip()
        parts = self._split(url)
        current = self.root

        for part in parts:
            key = WILDCARD if self._is_param(part) else part
            if key not in current.children:
                current.children[key] = Node(part)
            current = current.children[key]

        current.marker = True
        current.handler = handler or f"handler:{url}"

    def search_url(self, url: str) -> bool:
        """
        Return True if this exact URL (params considered wildcards) exists.
        Time: O(D).
        """
        return self._match_node(url) is not None

    def route(self, url: str) -> Optional[Dict]:
        """
        Match a concrete URL against registered routes.
        Returns {'url': matched_pattern, 'params': {name: value}, 'handler': ...}
        or None if no match.
        Time: O(D).
        """
        parts = self._split(url.strip())
        result = self._route_recursive(self.root, parts, 0, {})
        return result

    def match_urls(self, prefix: str) -> List[str]:
        """
        Return all registered URLs that start with prefix.
        Time: O(D + K).
        """
        parts = self._split(prefix.strip())
        current = self.root
        for part in parts:
            child = current.find_child(part) or current.find_child(WILDCARD)
            if child is None:
                return []
            current = child
        results: List[str] = []
        self._collect(current, "/".join(parts), results)
        return results

    def delete_url(self, url: str) -> bool:
        """
        Remove a URL from the Trie. Returns True if deleted.
        Time: O(D).
        """
        if not self.search_url(url):
            return False
        parts = self._split(url.strip())
        self._delete(self.root, parts, 0)
        return True

    def list_all_routes(self) -> List[str]:
        """Return all registered URL patterns. Time: O(N)."""
        results: List[str] = []
        self._collect(self.root, "", results)
        return results

    # ── Private Helpers ─────────────────────────────────────────────────

    def _match_node(self, url: str) -> Optional[Node]:
        parts = self._split(url.strip())
        current = self.root
        for part in parts:
            key = WILDCARD if self._is_param(part) else part
            child = current.find_child(key)
            if child is None:
                return None
            current = child
        return current if current.marker else None

    def _route_recursive(
        self,
        node: Node,
        parts: List[str],
        depth: int,
        params: Dict[str, str],
    ) -> Optional[Dict]:
        if depth == len(parts):
            if node.marker:
                return {
                    "handler": node.handler,
                    "params": params,
                }
            return None

        segment = parts[depth]

        # 1. Try exact match first (higher priority)
        if segment in node.children:
            result = self._route_recursive(node.children[segment], parts, depth + 1, params)
            if result:
                return result

        # 2. Try wildcard match
        if WILDCARD in node.children:
            wildcard_node = node.children[WILDCARD]
            param_name = wildcard_node.content.lstrip(":")  # e.g. "id" from ":id"
            new_params = {**params, param_name: segment}
            result = self._route_recursive(wildcard_node, parts, depth + 1, new_params)
            if result:
                return result

        return None

    def _collect(self, node: Node, prefix: str, res: List[str]) -> None:
        if node.marker:
            res.append(prefix)
        for key, child in node.children.items():
            segment = child.content
            new_prefix = f"{prefix}/{segment}" if prefix else segment
            self._collect(child, new_prefix, res)

    def _delete(self, current: Node, parts: List[str], index: int) -> bool:
        if index == len(parts):
            if not current.marker:
                return False
            current.marker = False
            current.handler = None
            return len(current.children) == 0
        part = parts[index]
        key = WILDCARD if self._is_param(part) else part
        child = current.find_child(key)
        if child is None:
            return False
        should_delete = self._delete(child, parts, index + 1)
        if should_delete:
            current.remove_child(key)
            return len(current.children) == 0 and not current.marker
        return False


def main():
    print("URL Routing — Segment Trie with Wildcards\n")

    router = URLRoutingTrie()

    # Register routes (like an Express.js / FastAPI app)
    routes = [
        ("https://example.com/home",                     "home_page"),
        ("https://example.com/about",                    "about_page"),
        ("https://example.com/user/:id",                 "user_profile"),
        ("https://example.com/user/:id/posts",           "user_posts"),
        ("https://example.com/user/:id/posts/:postId",   "user_post_detail"),
        ("https://sample.com/shop",                      "shop_page"),
        ("https://sample.com/shop/:category",            "shop_category"),
    ]

    print("Registering routes:")
    for url, handler in routes:
        router.add_url(url, handler)
        print(f"  + {url}  [{handler}]")

    # Test exact routing with param extraction
    print("\nRouting requests:")
    test_urls = [
        "https://example.com/home",
        "https://example.com/user/42",
        "https://example.com/user/42/posts",
        "https://example.com/user/42/posts/99",
        "https://sample.com/shop/electronics",
        "https://example.com/does/not/exist",
    ]
    for url in test_urls:
        result = router.route(url)
        if result:
            print(f"  '{url}'")
            print(f"    handler : {result['handler']}")
            if result["params"]:
                print(f"    params  : {result['params']}")
        else:
            print(f"  '{url}'  -> 404 Not Found")

    # Prefix listing
    print("\nAll routes under 'https://example.com/user/:id':")
    matches = router.match_urls("https://example.com/user/:id")
    for m in matches:
        print(f"  {m}")

    print("\nAll registered routes:")
    for r in router.list_all_routes():
        print(f"  {r}")


if __name__ == "__main__":
    main()
