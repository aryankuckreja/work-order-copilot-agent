# Demo: work-order flag checks on synthetic data

An independent recreation of the nightly verification idea. All data is randomly generated; no company data, queries or code are used.

```bash
python3 run_demo.py
```

- `generate_synthetic.py` builds a 6,000-row history and 40 new work orders, some with planted problems (wrong markup, site from another customer, missing field, unseen equipment).
- `flags.sql` builds a historical profile with CTEs, ranks markups per customer and trade with window functions, and labels each new work order.
- Ambiguous cases are labelled `MARKUP SPLIT` instead of being hidden, following the design principle in [../docs/verification-flags.md](../docs/verification-flags.md).

Requires only Python 3.8+ (SQLite with window functions ships with Python).
