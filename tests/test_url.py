"""tests/test_url.py — Unit Tests for url.py"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from url import URLRoutingTrie


@pytest.fixture
def router():
    r = URLRoutingTrie()
    r.add_url("https://example.com/home",                   "home")
    r.add_url("https://example.com/about",                  "about")
    r.add_url("https://example.com/user/:id",               "user_profile")
    r.add_url("https://example.com/user/:id/posts",         "user_posts")
    r.add_url("https://example.com/user/:id/posts/:postId", "post_detail")
    r.add_url("https://sample.com/shop/:category",          "shop_cat")
    return r


# ── Basic URL Operations ──────────────────────────────────────────────────

class TestAddAndSearch:
    def test_search_existing(self, router):
        assert router.search_url("https://example.com/home") is True

    def test_search_nonexistent(self, router):
        assert router.search_url("https://example.com/contact") is False

    def test_search_partial_not_found(self, router):
        assert router.search_url("https://example.com") is False

    def test_list_all_routes(self, router):
        routes = router.list_all_routes()
        assert len(routes) == 6


# ── Wildcard / Parameter Routing ──────────────────────────────────────────

class TestRouting:
    def test_exact_route(self, router):
        result = router.route("https://example.com/home")
        assert result is not None
        assert result["handler"] == "home"
        assert result["params"] == {}

    def test_single_param(self, router):
        result = router.route("https://example.com/user/42")
        assert result is not None
        assert result["handler"] == "user_profile"
        assert result["params"] == {"id": "42"}

    def test_nested_params(self, router):
        result = router.route("https://example.com/user/42/posts/99")
        assert result is not None
        assert result["handler"] == "post_detail"
        assert result["params"] == {"id": "42", "postId": "99"}

    def test_no_match_returns_none(self, router):
        result = router.route("https://example.com/does/not/exist")
        assert result is None

    def test_exact_beats_wildcard(self, router):
        """Exact segment should take priority over wildcard."""
        r = URLRoutingTrie()
        r.add_url("/user/profile", "exact_profile")
        r.add_url("/user/:id",     "param_profile")
        result = r.route("/user/profile")
        assert result["handler"] == "exact_profile"

    def test_wildcard_fallback(self, router):
        result = router.route("https://sample.com/shop/electronics")
        assert result is not None
        assert result["params"] == {"category": "electronics"}


# ── Prefix Matching ───────────────────────────────────────────────────────

class TestPrefixMatch:
    def test_prefix_returns_multiple(self, router):
        matches = router.match_urls("https://example.com/user/:id")
        assert len(matches) >= 2  # /user/:id, /user/:id/posts, /user/:id/posts/:postId

    def test_prefix_no_match(self, router):
        matches = router.match_urls("https://example.com/xyz")
        assert matches == []


# ── Delete ────────────────────────────────────────────────────────────────

class TestDelete:
    def test_delete_existing(self, router):
        assert router.delete_url("https://example.com/home") is True
        assert router.search_url("https://example.com/home") is False

    def test_delete_nonexistent(self, router):
        assert router.delete_url("https://example.com/nope") is False

    def test_delete_child_keeps_parent(self, router):
        router.delete_url("https://example.com/user/:id/posts")
        # parent still exists
        assert router.search_url("https://example.com/user/:id") is True

    def test_delete_updates_list(self, router):
        before = len(router.list_all_routes())
        router.delete_url("https://example.com/about")
        assert len(router.list_all_routes()) == before - 1
