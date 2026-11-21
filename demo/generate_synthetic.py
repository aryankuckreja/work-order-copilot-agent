"""Generate a synthetic work-order history in SQLite.

Everything here is invented: customers, sites, trades and markups are random.
The shape (customer, site, trade, markup, equipment) mirrors the kind of data the
real agent used, so the flag checks in flags.sql behave realistically.
"""
import random
import sqlite3
from datetime import date, timedelta

TRADES = ["HVAC", "ELECTRICAL", "PLUMBING", "CONTROLS", "REFRIGERATION"]
MARKUPS = [0.10, 0.15, 0.20, 0.25]


def build(conn: sqlite3.Connection, n_history: int = 6000, n_new: int = 40, seed: int = 7) -> None:
    rng = random.Random(seed)
    conn.executescript(
        """
        DROP TABLE IF EXISTS work_orders;
        CREATE TABLE work_orders (
            wo_id      INTEGER PRIMARY KEY,
            opened_on  TEXT NOT NULL,
            customer   TEXT NOT NULL,
            site       TEXT NOT NULL,
            trade      TEXT NOT NULL,
            markup     REAL,
            equipment  TEXT,
            is_new     INTEGER NOT NULL DEFAULT 0
        );
        """
    )

    customers = {}
    for c in range(1, 26):
        name = f"CUST-{c:03d}"
        sites = [f"{name}-SITE-{s}" for s in range(1, rng.randint(2, 6))]
        # Each customer has a preferred markup per trade; some groups are deliberately split.
        pref = {t: rng.choice(MARKUPS) for t in TRADES}
        split = {t: rng.random() < 0.2 for t in TRADES}
        customers[name] = (sites, pref, split)

    start = date(2021, 11, 1)
    rows = []
    for i in range(n_history):
        cust = rng.choice(list(customers))
        sites, pref, split = customers[cust]
        trade = rng.choice(TRADES)
        markup = rng.choice(MARKUPS) if split[trade] else pref[trade]
        if rng.random() < 0.03:
            markup = rng.choice(MARKUPS)  # realistic noise
        site = rng.choice(sites)
        equipment = f"{trade[:3]}-{rng.randint(1, 4)}"
        opened = start + timedelta(days=rng.randint(0, 5 * 365))
        rows.append((opened.isoformat(), cust, site, trade, markup, equipment, 0))

    today = start + timedelta(days=5 * 365 + 1)
    for i in range(n_new):
        cust = rng.choice(list(customers))
        sites, pref, split = customers[cust]
        trade = rng.choice(TRADES)
        markup = pref[trade]
        site = rng.choice(sites)
        equipment = f"{trade[:3]}-{rng.randint(1, 4)}"
        roll = rng.random()
        if roll < 0.15:
            markup = rng.choice([m for m in MARKUPS if m != pref[trade]])   # wrong markup
        elif roll < 0.22:
            site = f"{rng.choice(list(customers))}-SITE-1"                   # site from another customer
        elif roll < 0.27:
            markup = None                                                     # missing field
        elif roll < 0.31:
            equipment = f"{trade[:3]}-9"                                      # never-seen equipment
        rows.append((today.isoformat(), cust, site, trade, markup, equipment, 1))

    conn.executemany(
        "INSERT INTO work_orders (opened_on, customer, site, trade, markup, equipment, is_new) VALUES (?,?,?,?,?,?,?)",
        rows,
    )
    conn.commit()
