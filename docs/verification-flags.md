# Nightly verification flags

Each night a query scores newly opened work orders against five years of history for the same customer, site and trade. It uses common table expressions to build the historical profile and window functions to rank values within each group.

## Flag design principles

1. **A flag is a question, not a verdict.** The data cannot always tell an entry mistake from a legitimate exception, which means flags say what looks unusual and why.
2. **Never suppress ambiguity.** When a markup did not match history, the check could not know whether it was wrong or a special arrangement. Instead of hiding those cases, they were split into two categories:
   - `MARKUP`: the value does not appear in this customer and trade's history at all.
   - `MARKUP SPLIT`: the history itself is split between several values, which makes a mismatch is less suspicious.
3. **Severity reflects consequence.** Applying the same thinking to equipment flags turned 16 equal-weight flags into 1 serious and 15 minor, which made the report reviewable in minutes.

## Flag types (generalised)

| Type | Fires when |
|---|---|
| Unknown value | A field value never appears in history for this customer |
| Rare value | A value appears in less than a small share of history for the group |
| Markup mismatch | Markup differs from the dominant value for customer and trade |
| Markup split | History for the group has no dominant markup |
| Trade mismatch | Trade is unusual for the site |
| Site mismatch | Site does not belong to the customer in history |
| Equipment mismatch | Equipment code is unusual for the site, ranked by severity |
| Missing field | A required field is blank |
| New combination | A customer, site and trade combination never seen before |

## Results

- 7-day run: 43 flags. 10-day run: 62 flags.
- Each flag carries the historical evidence (counts and shares) so a reviewer can decide quickly.

The `demo/` folder recreates several of these checks on synthetic data.
