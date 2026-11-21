-- Flag checks on synthetic data (SQLite). Same style as the real nightly
-- verification: CTEs build a historical profile, window functions rank values.

WITH history AS (
    SELECT * FROM work_orders WHERE is_new = 0
),
markup_profile AS (
    SELECT customer, trade, markup,
           COUNT(*) AS n,
           SUM(COUNT(*)) OVER (PARTITION BY customer, trade) AS total,
           ROW_NUMBER() OVER (PARTITION BY customer, trade ORDER BY COUNT(*) DESC) AS rnk
    FROM history
    GROUP BY customer, trade, markup
),
dominant AS (
    SELECT customer, trade, markup AS top_markup, 1.0 * n / total AS top_share
    FROM markup_profile WHERE rnk = 1
),
seen_markup AS (
    SELECT DISTINCT customer, trade, markup FROM history
),
customer_sites AS (
    SELECT DISTINCT customer, site FROM history
),
site_equipment AS (
    SELECT DISTINCT site, equipment FROM history
),
new_wo AS (
    SELECT * FROM work_orders WHERE is_new = 1
)
SELECT w.wo_id, w.customer, w.site, w.trade, w.markup, w.equipment,
       CASE
           WHEN w.markup IS NULL THEN 'MISSING FIELD'
           WHEN cs.site IS NULL THEN 'SITE MISMATCH'
           WHEN w.markup <> d.top_markup AND d.top_share >= 0.6 AND sm.markup IS NULL THEN 'MARKUP (never seen)'
           WHEN w.markup <> d.top_markup AND d.top_share >= 0.6 THEN 'MARKUP'
           WHEN w.markup <> d.top_markup AND d.top_share < 0.6 THEN 'MARKUP SPLIT'
           WHEN se.equipment IS NULL THEN 'EQUIPMENT (minor)'
       END AS flag,
       ROUND(d.top_share, 2) AS history_top_share,
       d.top_markup AS history_top_markup
FROM new_wo w
LEFT JOIN dominant d       ON d.customer = w.customer AND d.trade = w.trade
LEFT JOIN seen_markup sm   ON sm.customer = w.customer AND sm.trade = w.trade AND sm.markup = w.markup
LEFT JOIN customer_sites cs ON cs.customer = w.customer AND cs.site = w.site
LEFT JOIN site_equipment se ON se.site = w.site AND se.equipment = w.equipment
WHERE flag IS NOT NULL
ORDER BY CASE flag WHEN 'MISSING FIELD' THEN 1 WHEN 'SITE MISMATCH' THEN 2 WHEN 'MARKUP (never seen)' THEN 3 WHEN 'MARKUP' THEN 3
                   WHEN 'MARKUP SPLIT' THEN 4 ELSE 5 END, w.wo_id;
