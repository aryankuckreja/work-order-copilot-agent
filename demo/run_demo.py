"""Build synthetic data and print the flag report."""
import sqlite3
from pathlib import Path

from generate_synthetic import build


def main() -> None:
    conn = sqlite3.connect(":memory:")
    build(conn)
    query = Path(__file__).with_name("flags.sql").read_text()
    rows = conn.execute(query).fetchall()
    total_new = conn.execute("SELECT COUNT(*) FROM work_orders WHERE is_new = 1").fetchone()[0]

    print(f"Checked {total_new} new work orders against "
          f"{conn.execute('SELECT COUNT(*) FROM work_orders WHERE is_new = 0').fetchone()[0]} historical rows.")
    print(f"{len(rows)} flagged for review.\n")
    header = f"{'WO':>6}  {'CUSTOMER':<9} {'TRADE':<13} {'MARKUP':>6}  {'FLAG':<20} EVIDENCE"
    print(header)
    print("-" * len(header))
    for wo, cust, site, trade, markup, equip, flag, share, top in rows:
        m = "-" if markup is None else f"{markup:.2f}"
        evidence = f"history top {top:.2f} at {share:.0%}" if share is not None else ""
        print(f"{wo:>6}  {cust:<9} {trade:<13} {m:>6}  {flag:<20} {evidence}")


if __name__ == "__main__":
    main()
