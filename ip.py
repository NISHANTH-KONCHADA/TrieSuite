"""
ip.py — IP Address Routing via Binary Trie (Longest Prefix Match)
=================================================================
Models how real routers perform IP lookups.  IPv4 addresses are 32-bit
binary strings, so all operations are effectively O(1).

| Operation            | Time   | Space        |
|----------------------|--------|--------------|
| insert               | O(32)  | O(32) / route|
| exact_match          | O(32)  | O(1)         |
| longest_prefix_match | O(32)  | O(1)         |
| all_matching_prefixes| O(32)  | O(k)         |

This mirrors the Longest Prefix Match (LPM) algorithm used in BGP/OSPF
routers and the Linux kernel routing table.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple

Route = Tuple[str, str, str]  # (network_addr, subnet_mask, label)


class Node:
    """A node in the binary (bit-level) IP routing Trie."""
    __slots__ = ("marker", "children", "data")

    def __init__(self):
        self.marker: bool = False
        self.children: Dict[int, "Node"] = {}
        self.data: Optional[Route] = None


class IPRoutingTrie:
    """
    Binary Trie for IP routing table lookups.
    Implements Longest Prefix Match — the algorithm every real router uses.
    """

    def __init__(self):
        self.root = Node()
        self._routes: List[Route] = []

    def insert(self, network: str, mask: str, label: str = "") -> None:
        """
        Insert a network route.  Mask is dotted-decimal (e.g. 255.255.255.0).
        Time: O(32).
        """
        binary = self._ip_to_bits(network)
        prefix_len = sum(
            int(b)
            for octet in mask.split(".")
            for b in format(int(octet), "08b")
        )
        route: Route = (network, mask, label or f"Network {network}/{prefix_len}")
        self._routes.append(route)

        current = self.root
        for i, bit in enumerate(binary):
            if i == prefix_len:
                break
            if bit not in current.children:
                current.children[bit] = Node()
            current = current.children[bit]
        current.marker = True
        current.data = route

    def insert_cidr(self, cidr: str, label: str = "") -> None:
        """
        Insert a route in CIDR notation, e.g. '192.168.1.0/24'.
        """
        try:
            network, prefix_str = cidr.split("/")
            prefix_len = int(prefix_str)
            mask = self._prefix_to_mask(prefix_len)
            self.insert(network, mask, label)
        except ValueError:
            raise ValueError(f"Invalid CIDR notation: '{cidr}'")

    def exact_match(self, ip: str) -> Optional[Route]:
        """
        Return the route whose prefix exactly matches the full 32-bit IP.
        Time: O(32).
        """
        binary = self._ip_to_bits(ip)
        current = self.root
        for bit in binary:
            if bit not in current.children:
                return None
            current = current.children[bit]
        return current.data if current.marker else None

    def longest_prefix_match(self, ip: str) -> Optional[Route]:
        """
        Return the MOST SPECIFIC route for an IP (longest matching prefix).
        This is exactly what a real router does when forwarding a packet.
        Time: O(32).
        """
        binary = self._ip_to_bits(ip)
        current = self.root
        best_match: Optional[Route] = None

        for bit in binary:
            if current.marker:
                best_match = current.data
            if bit not in current.children:
                break
            current = current.children[bit]

        # Check the final node
        if current.marker:
            best_match = current.data

        return best_match

    def all_matching_prefixes(self, ip: str) -> List[Route]:
        """
        Return ALL routes whose prefix matches the IP, least→most specific.
        Time: O(32).
        """
        binary = self._ip_to_bits(ip)
        current = self.root
        matches: List[Route] = []

        for bit in binary:
            if current.marker and current.data:
                matches.append(current.data)
            if bit not in current.children:
                break
            current = current.children[bit]

        return matches

    def show_routing_table(self) -> None:
        """Print a formatted routing table."""
        print(f"\n{'Network':<18} {'Mask':<18} {'Label'}")
        print("─" * 60)
        for net, mask, label in self._routes:
            print(f"{net:<18} {mask:<18} {label}")
        print()

    # ── Private Helpers ─────────────────────────────────────────────────

    @staticmethod
    def _ip_to_bits(ip: str) -> List[int]:
        """Convert dotted-decimal IP to a list of 32 ints (0 or 1)."""
        try:
            return [
                int(b)
                for octet in ip.strip().split(".")
                for b in format(int(octet), "08b")
            ]
        except (ValueError, AttributeError):
            raise ValueError(f"Invalid IP address: '{ip}'")

    @staticmethod
    def _prefix_to_mask(prefix_len: int) -> str:
        """Convert CIDR prefix length (e.g. 24) to dotted mask (255.255.255.0)."""
        bits = ("1" * prefix_len).ljust(32, "0")
        return ".".join(str(int(bits[i:i+8], 2)) for i in range(0, 32, 8))


def load_test_cases(file_path: str) -> Tuple[List[Tuple[str, str]], List[str]]:
    """Load network addresses and test IPs from a structured text file."""
    networks: List[Tuple[str, str]] = []
    ips: List[str] = []
    section = None

    try:
        with open(file_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "Network addresses" in line:
                    section = "networks"
                elif "IP addresses" in line:
                    section = "ips"
                elif section == "networks":
                    parts = line.split()
                    if len(parts) == 2:
                        networks.append((parts[0], parts[1]))
                elif section == "ips":
                    ips.append(line)
    except FileNotFoundError:
        print(f"[ERROR] File '{file_path}' not found.")

    return networks, ips


def main():
    print("IP Routing — Binary Trie (Longest Prefix Match)\n")

    trie = IPRoutingTrie()
    networks, ip_addresses = load_test_cases("test_cases.txt")

    for net, mask in networks:
        trie.insert(net, mask)

    trie.show_routing_table()

    for ip in ip_addresses:
        lpm = trie.longest_prefix_match(ip)
        all_matches = trie.all_matching_prefixes(ip)
        print(f"IP: {ip}")
        if lpm:
            print(f"  Best Route (LPM) : {lpm[0]}/{lpm[1]}")
        else:
            print(f"  No route found   : packet would be dropped")
        if len(all_matches) > 1:
            print(f"  All prefix matches: {[m[0] for m in all_matches]}")
        print()


if __name__ == "__main__":
    main()
