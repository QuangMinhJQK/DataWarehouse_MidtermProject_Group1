-- Source: docs/source/Gold_Warehouse_Huong_dan_chi_tiet (3).docx
-- BEGIN E
CREATE OR ALTER VIEW mart.sales_line_approved AS
SELECT l.*,p.source_currency,p.report_currency,p.metric_version,
 o.last_complete_date,o.published_at,
 CASE WHEN p.source_currency=p.report_currency THEN CAST(1 AS decimal(28,10))
 ELSE r.average_rate END report_rate,
 CASE WHEN p.source_currency=p.report_currency THEN 'BASE_EQUALS_REPORT'
 WHEN r.currency_rate_id IS NULL THEN 'NO_RATE_MATCH' ELSE 'CONVERTED' END fx_status,
 CAST(l.net_line_amount * CASE WHEN p.source_currency=p.report_currency
 THEN 1 ELSE r.average_rate END AS decimal(28,6)) report_net_amount
FROM fact.sales_order_line l
JOIN ops.publication o ON l._gold_run_id=o.run_id
JOIN ref.policy p ON o.policy_id=p.policy_id AND p.approved=1
JOIN ref.order_status s ON s.policy_id=p.policy_id
 AND s.status_code=l.order_status AND s.include_sales=1
JOIN dim.date d ON d.date_key=l.order_date_key
LEFT JOIN fact.currency_rate r ON r.rate_date=d.full_date
 AND r.from_currency_key=p.source_currency
 AND r.to_currency_key=p.report_currency
WHERE d.full_date<=o.last_complete_date;
GO
CREATE OR ALTER VIEW mart.sales_product_day AS
SELECT order_date_key,product_key,territory_key,online_order_flag,
 SUM(order_qty) sold_qty,SUM(net_line_amount) net_amount,
 CASE WHEN SUM(CASE WHEN fx_status='NO_RATE_MATCH' THEN 1 ELSE 0 END)>0 THEN NULL ELSE SUM(report_net_amount) END report_net_amount,
 SUM(discount_amount) discount_amount,
 SUM(gross_line_amount) gross_amount,
 SUM(estimated_standard_margin_amount) estimated_margin,
 SUM(CASE WHEN cost_match_status='MATCHED' THEN net_line_amount ELSE 0 END) net_with_cost,
 SUM(CASE WHEN fx_status='NO_RATE_MATCH' THEN 1 ELSE 0 END) fx_missing_lines,
 COUNT_BIG(*) line_count,COUNT(DISTINCT sales_order_id) order_count
FROM mart.sales_line_approved
GROUP BY order_date_key,product_key,territory_key,online_order_flag;
GO
CREATE OR ALTER VIEW mart.customer_performance AS
SELECT customer_key,MIN(d.full_date) first_order_date,
 MAX(d.full_date) last_order_date,COUNT(DISTINCT sales_order_id) order_count,
 SUM(net_line_amount) net_amount,SUM(order_qty) sold_qty,
 SUM(estimated_standard_margin_amount) estimated_margin
FROM mart.sales_line_approved l JOIN dim.date d ON d.date_key=l.order_date_key
GROUP BY customer_key;
GO
CREATE OR ALTER VIEW mart.customer_rfm_current AS
SELECT c.*,o.last_complete_date as_of_date,
 DATEDIFF(day,c.last_order_date,o.last_complete_date) recency_days
FROM mart.customer_performance c CROSS JOIN ops.publication o;
GO
CREATE OR ALTER VIEW mart.order_operations AS
SELECT h.*,o.last_complete_date,o.published_at
FROM fact.sales_order h JOIN ops.publication o ON h._gold_run_id=o.run_id;
GO
CREATE OR ALTER VIEW mart.quota_performance AS
WITH sales AS (
 SELECT l.sales_person_key,DATEFROMPARTS(YEAR(d.full_date),
 3*((MONTH(d.full_date)-1)/3)+1,1) quota_quarter,SUM(l.net_line_amount) actual_net
 FROM mart.sales_line_approved l JOIN dim.date d ON d.date_key=l.order_date_key
 GROUP BY l.sales_person_key,DATEFROMPARTS(YEAR(d.full_date),3*((MONTH(d.full_date)-1)/3)+1,1)
)
SELECT COALESCE(q.sales_person_key,s.sales_person_key) sales_person_key,
 COALESCE(q.quota_quarter,s.quota_quarter) quota_quarter,
 q.sales_quota,s.actual_net,
 s.actual_net/NULLIF(q.sales_quota,0) attainment_rate,
 CASE WHEN q.sales_person_key IS NULL THEN 'NO_QUOTA'
 WHEN s.sales_person_key IS NULL THEN 'NO_SALES' ELSE 'MATCHED' END match_status
FROM fact.sales_quota q FULL JOIN sales s
 ON q.sales_person_key=s.sales_person_key AND q.quota_quarter=s.quota_quarter;
GO
CREATE OR ALTER VIEW mart.price_realization AS
SELECT l.sales_order_id,l.sales_order_detail_id,l.product_key,
 l.order_date_key,l.order_qty,l.unit_price,l.unit_price_discount,
 l.net_line_amount,h.list_price list_price_at_order,
 CASE WHEN h.product_key IS NULL THEN 'NO_PRICE_MATCH' ELSE 'MATCHED' END price_match_status,
 CAST(l.net_line_amount/NULLIF(l.order_qty,0) AS decimal(28,6)) realized_unit_price,
 l.net_line_amount/NULLIF(l.order_qty*h.list_price,0) realization_rate
FROM mart.sales_line_approved l JOIN dim.date d ON d.date_key=l.order_date_key
LEFT JOIN fact.product_price_history h ON h.product_key=l.product_key
 AND d.full_date>=CAST(h.start_date AS date)
 AND (h.end_date IS NULL OR d.full_date<=CAST(h.end_date AS date));
GO
CREATE OR ALTER VIEW mart.offer_performance AS
SELECT l.special_offer_key,COUNT_BIG(*) line_count,
 COUNT(DISTINCT l.sales_order_id) order_count,SUM(l.net_line_amount) net_amount,
 SUM(l.discount_amount) discount_amount,
 SUM(CASE WHEN b.product_key IS NULL THEN 1 ELSE 0 END) invalid_offer_product_lines
FROM mart.sales_line_approved l LEFT JOIN fact.offer_product b
 ON b.special_offer_key=l.special_offer_key AND b.product_key=l.product_key
GROUP BY l.special_offer_key;
GO
CREATE OR ALTER VIEW mart.inventory_product_current AS
SELECT i.*,p.product_name,p.category_name,p.safety_stock_level,p.reorder_point,
 o.inventory_observed_at,
 CASE WHEN DATEDIFF(hour,o.inventory_observed_at,SYSUTCDATETIME())>r.stock_max_age_hours
 THEN 'STALE' ELSE 'WITHIN_CONFIGURED_AGE' END freshness_status,
 CASE WHEN i.total_stock_qty IS NULL THEN 'NO_INVENTORY_RECORD'
 WHEN i.total_stock_qty<=0 THEN 'OUT_OF_STOCK'
 WHEN i.total_stock_qty<p.safety_stock_level THEN 'BELOW_SAFETY_STOCK'
 WHEN i.total_stock_qty<=p.reorder_point THEN 'REORDER' ELSE 'NORMAL' END alert_status
FROM fact.inventory_product_current i JOIN dim.product p ON i.product_key=p.product_key
JOIN ops.publication o ON o.run_id=i._gold_run_id
JOIN ref.policy r ON r.policy_id=o.policy_id;
GO
CREATE OR ALTER VIEW mart.data_health AS
SELECT o.*,p.source_currency,p.report_currency,p.metric_version,p.stock_max_age_hours,
 (SELECT COUNT_BIG(*) FROM fact.sales_order_line WHERE cost_match_status='NO_COST_MATCH') missing_cost_lines,
 (SELECT COUNT_BIG(*) FROM mart.sales_line_approved WHERE fx_status='NO_RATE_MATCH') missing_fx_lines
FROM ops.publication o JOIN ref.policy p ON p.policy_id=o.policy_id;
GO
CREATE OR ALTER VIEW ml.sales_input AS
SELECT l.product_key,d.full_date business_date,l.order_qty,l.net_line_amount,
 l.sales_order_id,l._gold_run_id source_gold_run_id
FROM mart.sales_line_approved l JOIN dim.date d ON d.date_key=l.order_date_key
JOIN ops.publication o ON o.run_id=l._gold_run_id
WHERE d.full_date<=o.last_complete_date;
GO
CREATE OR ALTER VIEW ml.product_eligibility_input AS
SELECT product_key,active_start,active_end,finished_goods_flag
FROM dim.product_eligibility;
GO
CREATE OR ALTER VIEW agent.sales AS SELECT * FROM mart.sales_line_approved;
GO
CREATE OR ALTER VIEW agent.inventory AS SELECT * FROM mart.inventory_product_current;
GO
CREATE OR ALTER VIEW agent.customer_summary AS
SELECT customer_key,order_count,net_amount,first_order_date,last_order_date
FROM mart.customer_performance;
GO
CREATE OR ALTER VIEW agent.forecast AS
WITH ranked AS (
 SELECT f.*,ROW_NUMBER() OVER(PARTITION BY product_key,cutoff_date,horizon_days
 ORDER BY p.published_at DESC,f.scored_at DESC) rn
 FROM ml.forecast_prediction f JOIN ops.scoring_publication p
 ON p.scoring_run_id=f.scoring_run_id
)
SELECT product_key,cutoff_date,horizon_days,predicted_qty,baseline_qty,
 model_version,dataset_id,source_gold_run_id,availability_mode,
 scored_at,valid_until,
 CASE WHEN availability_mode='RECONSTRUCTED' THEN 'HISTORICAL_DEMO'
 WHEN valid_until<SYSUTCDATETIME() THEN 'EXPIRED'
 WHEN source_gold_run_id<>(SELECT run_id FROM ops.publication) THEN 'SOURCE_CHANGED'
 ELSE 'VALID' END prediction_status
FROM ranked WHERE rn=1;
GO

-- END E
