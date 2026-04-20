"""
Polymarket Open Markets Loader
===============================
Fetches all currently open (active) markets from the Polymarket Gamma API.

The Gamma API (https://gamma-api.polymarket.com) is Polymarket's public,
read-only REST API for market discovery. No authentication is required.

Usage:
    python polymarket_loader.py                  # print summary to console
    python polymarket_loader.py --json           # dump full JSON to stdout
    python polymarket_loader.py --csv polymarket_05_03.csv    # export to CSV
    python polymarket_loader.py --limit 50       # fetch only 50 markets

Requirements:
    pip install requests
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from dataclasses import dataclass, field, asdict
from typing import Any

import requests

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
GAMMA_API_BASE = "https://gamma-api.polymarket.com"
EVENTS_ENDPOINT = f"{GAMMA_API_BASE}/events"
MARKETS_ENDPOINT = f"{GAMMA_API_BASE}/markets"

DEFAULT_PAGE_SIZE = 100  # max items per request
REQUEST_DELAY = 0.15     # seconds between paginated requests (stay under rate limits)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------
@dataclass
class MarketOutcome:
    """A single outcome (e.g. Yes / No) of a market."""
    name: str
    price: float | None = None
    token_id: str = ""


@dataclass
class Market:
    """Represents one Polymarket prediction market."""
    market_id: str = ""
    condition_id: str = ""
    question: str = ""
    slug: str = ""
    description: str = ""
    end_date: str = ""
    created_at: str = ""
    outcomes: list[MarketOutcome] = field(default_factory=list)
    volume: float = 0.0
    volume_24h: float = 0.0
    liquidity: float = 0.0
    active: bool = True
    closed: bool = False
    accepting_orders: bool = True
    event_slug: str = ""
    event_title: str = ""
    image: str = ""
    icon: str = ""
    tags: list[str] = field(default_factory=list)

    # ---- helpers ----
    @property
    def yes_price(self) -> float | None:
        """Return the 'Yes' outcome price, or the first outcome price."""
        for o in self.outcomes:
            if o.name.lower() == "yes":
                return o.price
        return self.outcomes[0].price if self.outcomes else None

    @property
    def probability_pct(self) -> str:
        """Human-readable probability string."""
        p = self.yes_price
        return f"{p * 100:.1f}%" if p is not None else "N/A"


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------
def _safe_float(val: Any, default: float = 0.0) -> float:
    """Convert a value to float, returning *default* on failure."""
    if val is None:
        return default
    try:
        return float(val)
    except (TypeError, ValueError):
        return default


def _parse_outcomes(raw: dict) -> list[MarketOutcome]:
    """Extract outcomes with prices from a raw market dict."""
    outcome_names: list[str] = []
    outcome_prices: list[float | None] = []

    # outcome names – stored as JSON-encoded list string or plain list
    raw_outcomes = raw.get("outcomes") or "[]"
    if isinstance(raw_outcomes, str):
        try:
            outcome_names = json.loads(raw_outcomes)
        except json.JSONDecodeError:
            outcome_names = [raw_outcomes]
    elif isinstance(raw_outcomes, list):
        outcome_names = raw_outcomes

    # outcome prices – same encoding pattern
    raw_prices = raw.get("outcomePrices") or "[]"
    if isinstance(raw_prices, str):
        try:
            outcome_prices = [_safe_float(p) for p in json.loads(raw_prices)]
        except json.JSONDecodeError:
            outcome_prices = []
    elif isinstance(raw_prices, list):
        outcome_prices = [_safe_float(p) for p in raw_prices]

    # token IDs
    raw_tokens = raw.get("clobTokenIds") or "[]"
    if isinstance(raw_tokens, str):
        try:
            token_ids = json.loads(raw_tokens)
        except json.JSONDecodeError:
            token_ids = []
    elif isinstance(raw_tokens, list):
        token_ids = raw_tokens
    else:
        token_ids = []

    results: list[MarketOutcome] = []
    for i, name in enumerate(outcome_names):
        price = outcome_prices[i] if i < len(outcome_prices) else None
        tid = token_ids[i] if i < len(token_ids) else ""
        results.append(MarketOutcome(name=str(name), price=price, token_id=str(tid)))
    return results


def _parse_market(raw: dict, event_info: dict | None = None) -> Market:
    """Convert a raw JSON market dict into a Market dataclass."""
    outcomes = _parse_outcomes(raw)
    tags_raw = raw.get("tags") or []
    tag_labels = []
    if isinstance(tags_raw, list):
        for t in tags_raw:
            if isinstance(t, dict):
                tag_labels.append(t.get("label", t.get("slug", "")))
            else:
                tag_labels.append(str(t))

    event_slug = ""
    event_title = ""
    if event_info:
        event_slug = event_info.get("slug", "")
        event_title = event_info.get("title", "")

    return Market(
        market_id=str(raw.get("id", "")),
        condition_id=str(raw.get("conditionId", "")),
        question=raw.get("question", ""),
        slug=raw.get("slug", ""),
        description=raw.get("description", ""),
        end_date=raw.get("endDate", ""),
        created_at=raw.get("createdAt", ""),
        outcomes=outcomes,
        volume=_safe_float(raw.get("volumeNum") or raw.get("volume")),
        volume_24h=_safe_float(raw.get("volume24hr")),
        liquidity=_safe_float(raw.get("liquidityNum") or raw.get("liquidity")),
        active=bool(raw.get("active", True)),
        closed=bool(raw.get("closed", False)),
        accepting_orders=bool(raw.get("acceptingOrders", True)),
        event_slug=event_slug,
        event_title=event_title,
        image=raw.get("image", ""),
        icon=raw.get("icon", ""),
        tags=tag_labels,
    )


# ---------------------------------------------------------------------------
# Core loader
# ---------------------------------------------------------------------------
def fetch_open_markets(
    max_markets: int | None = None,
    page_size: int = DEFAULT_PAGE_SIZE,
    verbose: bool = False,
) -> list[Market]:
    """
    Fetch all currently open markets from the Polymarket Gamma API.

    Uses the /events endpoint (with closed=false) because each event embeds
    its child markets, making this the most efficient retrieval strategy
    recommended by Polymarket's own documentation.

    Parameters
    ----------
    max_markets : int or None
        Stop after collecting this many markets. None = fetch everything.
    page_size : int
        Number of events per API page (max 100).
    verbose : bool
        Print progress to stderr.

    Returns
    -------
    list[Market]
        Parsed Market objects for every open market found.
    """
    all_markets: list[Market] = []
    offset = 0
    seen_ids: set[str] = set()

    while True:
        params = {
            "closed": "false",
            "order": "id",
            "ascending": "false",
            "limit": page_size,
            "offset": offset,
        }

        if verbose:
            print(
                f"[fetch] Requesting events offset={offset} limit={page_size} ...",
                file=sys.stderr,
            )

        try:
            resp = requests.get(EVENTS_ENDPOINT, params=params, timeout=30)
            resp.raise_for_status()
        except requests.RequestException as exc:
            print(f"[error] API request failed: {exc}", file=sys.stderr)
            break

        events: list[dict] = resp.json()
        if not events:
            break  # no more pages

        for event in events:
            child_markets = event.get("markets") or []
            for raw_mkt in child_markets:
                mid = str(raw_mkt.get("id", ""))
                if mid in seen_ids:
                    continue
                seen_ids.add(mid)

                # Only include markets that are actually open
                if raw_mkt.get("closed", False):
                    continue

                market = _parse_market(raw_mkt, event_info=event)
                all_markets.append(market)

                if max_markets and len(all_markets) >= max_markets:
                    if verbose:
                        print(
                            f"[fetch] Reached limit of {max_markets} markets.",
                            file=sys.stderr,
                        )
                    return all_markets

        if verbose:
            print(
                f"[fetch] ... got {len(events)} events, "
                f"total markets so far: {len(all_markets)}",
                file=sys.stderr,
            )

        # If fewer events returned than page_size, we've reached the end
        if len(events) < page_size:
            break

        offset += page_size
        time.sleep(REQUEST_DELAY)

    return all_markets


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------
def markets_to_dicts(markets: list[Market]) -> list[dict]:
    """Convert markets to plain dicts suitable for JSON serialization."""
    rows = []
    for m in markets:
        d = asdict(m)
        # Flatten outcomes for easier consumption
        d["outcomes"] = [
            {"name": o["name"], "price": o["price"], "token_id": o["token_id"]}
            for o in d["outcomes"]
        ]
        rows.append(d)
    return rows


def write_csv(markets: list[Market], path: str) -> None:
    """Write a flat CSV of markets (outcomes are comma-joined)."""
    fieldnames = [
        "market_id",
        "question",
        "event_title",
        "slug",
        "end_date",
        "yes_price",
        "probability",
        "volume",
        "volume_24h",
        "liquidity",
        "outcomes",
        "outcome_prices",
        "tags",
        "accepting_orders",
        "created_at",
    ]

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for m in markets:
            writer.writerow(
                {
                    "market_id": m.market_id,
                    "question": m.question,
                    "event_title": m.event_title,
                    "slug": m.slug,
                    "end_date": m.end_date,
                    "yes_price": m.yes_price,
                    "probability": m.probability_pct,
                    "volume": f"{m.volume:.2f}",
                    "volume_24h": f"{m.volume_24h:.2f}",
                    "liquidity": f"{m.liquidity:.2f}",
                    "outcomes": " | ".join(o.name for o in m.outcomes),
                    "outcome_prices": " | ".join(
                        f"{o.price:.4f}" if o.price is not None else "N/A"
                        for o in m.outcomes
                    ),
                    "tags": ", ".join(m.tags),
                    "accepting_orders": m.accepting_orders,
                    "created_at": m.created_at,
                }
            )
    print(f"Wrote {len(markets)} markets to {path}", file=sys.stderr)


def print_summary(markets: list[Market], top_n: int = 30) -> None:
    """Print a human-readable summary of the loaded markets."""
    print(f"\n{'=' * 70}")
    print(f"  Polymarket Open Markets — {len(markets)} total")
    print(f"{'=' * 70}\n")

    total_volume = sum(m.volume for m in markets)
    total_liquidity = sum(m.liquidity for m in markets)
    print(f"  Total volume (all time):  ${total_volume:,.0f}")
    print(f"  Total liquidity:          ${total_liquidity:,.0f}")
    print()

    # Sort by 24h volume descending
    sorted_markets = sorted(markets, key=lambda m: m.volume_24h, reverse=True)

    display = sorted_markets[:top_n]
    print(f"  Top {len(display)} by 24h volume:\n")
    print(f"  {'#':<4} {'Prob':>6}  {'24h Vol':>12}  {'Question'}")
    print(f"  {'—' * 4} {'—' * 6}  {'—' * 12}  {'—' * 40}")

    for i, m in enumerate(display, 1):
        q = m.question[:60] + ("…" if len(m.question) > 60 else "")
        print(f"  {i:<4} {m.probability_pct:>6}  ${m.volume_24h:>11,.0f}  {q}")

    print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Load all open Polymarket prediction markets via the Gamma API."
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output full market data as JSON to stdout.",
    )
    parser.add_argument(
        "--csv",
        metavar="FILE",
        help="Export markets to a CSV file.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of markets to fetch.",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=30,
        help="Number of top markets to show in summary (default: 30).",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print progress to stderr.",
    )
    args = parser.parse_args()

    markets = fetch_open_markets(
        max_markets=args.limit,
        verbose=args.verbose,
    )

    if args.json:
        json.dump(markets_to_dicts(markets), sys.stdout, indent=2, ensure_ascii=False)
        print()  # trailing newline
    elif args.csv:
        write_csv(markets, args.csv)
    else:
        print_summary(markets, top_n=args.top)


if __name__ == "__main__":
    main()